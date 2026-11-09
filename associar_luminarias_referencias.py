"""Gera a relação entre cada ID Nox e sua referência mais próxima.

O cálculo usa a fórmula de Haversine, que considera a curvatura da Terra.
O CSV de saída possui somente as colunas ``ID Nox``, ``tipo_ponto`` e
``nome``.
"""

from __future__ import annotations

from pathlib import Path
import unicodedata

import numpy as np
import pandas as pd
import os

PASTA = Path(os.environ["NOX_DADOS_DIR"]).resolve()

ARQUIVO_REFERENCIAS = PASTA / "referencias.csv"
ARQUIVO_LUMINARIAS = PASTA / "luminarias.csv"
ARQUIVO_SAIDA = PASTA / "resultado.csv"

def normalizar(texto: str) -> str:
    """Normaliza cabeçalhos para tolerar acentos, maiúsculas e espaços."""
    texto = unicodedata.normalize("NFKD", str(texto))
    texto = "".join(caractere for caractere in texto if not unicodedata.combining(caractere))
    return " ".join(texto.lower().strip().split())


def localizar_coluna(tabela: pd.DataFrame, alternativas: list[str], descricao: str) -> str:
    """Localiza uma coluna usando nomes alternativos aceitos."""
    colunas_normalizadas = {normalizar(coluna): coluna for coluna in tabela.columns}
    for alternativa in alternativas:
        coluna = colunas_normalizadas.get(normalizar(alternativa))
        if coluna is not None:
            return coluna
    raise ValueError(
        f"Não encontrei a coluna de {descricao}. "
        f"Colunas disponíveis: {list(tabela.columns)}"
    )


def ler_csv(caminho: Path) -> pd.DataFrame:
    """Lê CSV UTF-8 ou ANSI/Windows-1252, preservando IDs como texto."""
    for codificacao in ("utf-8-sig", "cp1252"):
        try:
            return pd.read_csv(caminho, encoding=codificacao, sep=None, engine="python", dtype="string")
        except UnicodeDecodeError:
            continue
    raise UnicodeDecodeError(
        "desconhecida", b"", 0, 1, f"Não foi possível ler {caminho.name} em UTF-8 ou Windows-1252."
    )


def converter_coordenadas(serie: pd.Series) -> np.ndarray:
    """Converte graus decimais escritos com vírgula ou ponto para números."""
    texto = serie.astype("string").str.strip().str.replace(",", ".", regex=False)
    return pd.to_numeric(texto, errors="coerce").to_numpy(dtype=float)


def haversine_metros(
    latitude_luminarias: np.ndarray,
    longitude_luminarias: np.ndarray,
    latitude_referencias: np.ndarray,
    longitude_referencias: np.ndarray,
) -> np.ndarray:
    """Retorna uma matriz de distâncias geodésicas, em metros."""
    raio_terra_m = 6_371_008.8
    lat_lum = np.deg2rad(latitude_luminarias)
    lon_lum = np.deg2rad(longitude_luminarias)
    lat_ref = np.deg2rad(latitude_referencias)
    lon_ref = np.deg2rad(longitude_referencias)

    delta_lat = lat_ref[None, :] - lat_lum[:, None]
    delta_lon = lon_ref[None, :] - lon_lum[:, None]
    a = (
        np.sin(delta_lat / 2) ** 2
        + np.cos(lat_lum[:, None]) * np.cos(lat_ref[None, :]) * np.sin(delta_lon / 2) ** 2
    )
    return 2 * raio_terra_m * np.arctan2(np.sqrt(a), np.sqrt(1 - a))


def calcular_vizinhos(
    luminarias: pd.DataFrame,
    referencias: pd.DataFrame,
    lat_lum_coluna: str,
    lon_lum_coluna: str,
    lat_ref_coluna: str,
    lon_ref_coluna: str,
    tamanho_bloco: int = 10_000,
) -> np.ndarray:
    """Devolve o índice da referência mais próxima para cada luminária.

    Luminárias sem coordenadas válidas (inclusive 0, 0) recebem -1.
    """
    lat_lum = converter_coordenadas(luminarias[lat_lum_coluna])
    lon_lum = converter_coordenadas(luminarias[lon_lum_coluna])
    lat_ref = converter_coordenadas(referencias[lat_ref_coluna])
    lon_ref = converter_coordenadas(referencias[lon_ref_coluna])

    luminarias_validas = (
        np.isfinite(lat_lum)
        & np.isfinite(lon_lum)
        & (np.abs(lat_lum) <= 90)
        & (np.abs(lon_lum) <= 180)
        & ~((lat_lum == 0) & (lon_lum == 0))
    )
    referencias_validas = (
        np.isfinite(lat_ref)
        & np.isfinite(lon_ref)
        & (np.abs(lat_ref) <= 90)
        & (np.abs(lon_ref) <= 180)
    )
    if not referencias_validas.any():
        raise ValueError("Nenhuma referência possui latitude e longitude válidas.")

    indices_ref_validos = np.flatnonzero(referencias_validas)
    indices_lum_validos = np.flatnonzero(luminarias_validas)
    vizinhos = np.full(len(luminarias), -1, dtype=int)

    for inicio in range(0, len(indices_lum_validos), tamanho_bloco):
        indices_bloco = indices_lum_validos[inicio : inicio + tamanho_bloco]
        distancias = haversine_metros(
            lat_lum[indices_bloco],
            lon_lum[indices_bloco],
            lat_ref[referencias_validas],
            lon_ref[referencias_validas],
        )
        posicao_mais_proxima = distancias.argmin(axis=1)
        vizinhos[indices_bloco] = indices_ref_validos[posicao_mais_proxima]

    return vizinhos


def main() -> None:
    referencias = ler_csv(ARQUIVO_REFERENCIAS)
    luminarias = ler_csv(ARQUIVO_LUMINARIAS)

    id_nox = localizar_coluna(luminarias, ["ID Nox", "ID_Nox", "id nox"], "ID Nox")
    nome_ref = localizar_coluna(referencias, ["nome", "nome do local", "localização"], "nome da referência")
    tipo_ref = localizar_coluna(
        referencias, ["tipo_ponto", "tipo", "tipo de ponto"], "tipo da referência"
    )
    lat_ref = localizar_coluna(referencias, ["latitude", "lat"], "latitude da referência")
    lon_ref = localizar_coluna(referencias, ["longitude", "lon", "lng"], "longitude da referência")
    lat_lum = localizar_coluna(luminarias, ["latitude", "lat"], "latitude da luminária")
    lon_lum = localizar_coluna(luminarias, ["longitude", "lon", "lng"], "longitude da luminária")

    # A tabela de origem tem várias leituras temporais para cada Nox. Como as
    # coordenadas são as mesmas dentro de cada ID, conservamos uma única linha.
    luminarias_unicas = luminarias.drop_duplicates(subset=id_nox, keep="first").copy()

    vizinhos = calcular_vizinhos(
        luminarias_unicas, referencias, lat_lum, lon_lum, lat_ref, lon_ref
    )

    resultado = pd.DataFrame({"ID Nox": luminarias_unicas[id_nox]})
    resultado["tipo_ponto"] = pd.NA
    resultado["nome"] = pd.NA
    possui_vizinho = vizinhos >= 0
    referencias_vizinhas = referencias.iloc[vizinhos[possui_vizinho]]
    resultado.loc[possui_vizinho, "tipo_ponto"] = referencias_vizinhas[tipo_ref].to_numpy()
    resultado.loc[possui_vizinho, "nome"] = referencias_vizinhas[nome_ref].to_numpy()

    resultado.to_csv(ARQUIVO_SAIDA, index=False, encoding="utf-8-sig")
    print("Arquivo de resultado criado com sucesso.")
    print(f"IDs Nox distintos: {len(resultado):,}".replace(",", "."))
    print(f"Sem coordenadas válidas: {(~possui_vizinho).sum():,}".replace(",", "."))


if __name__ == "__main__":
    main()
