from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


DATA_DIR = Path(__file__).parent / "datos"
OUTPUT_PATH = Path(__file__).parent / "percentiles_y_outliers_riesgo.png"
BOXPLOT_PATH = Path(__file__).parent / "boxplot_riesgo.png"


def calcular_riesgos() -> pd.DataFrame:
    inventarios = pd.read_csv(DATA_DIR / "inventarios.csv", parse_dates=["fecha"])
    productos = pd.read_csv(DATA_DIR / "productos.csv")
    inventarios["fecha"] = inventarios["fecha"].dt.normalize()

    ceros = inventarios.loc[
        inventarios["unidades_disponibles"].eq(0),
        ["tienda_id", "producto_id", "fecha"],
    ].drop_duplicates()
    productos = productos[["producto_id", "rotacion_esperada", "precio_lista", "costo"]]

    ventanas = []
    for fecha_corte in sorted(inventarios["fecha"].unique()):
        inicio = fecha_corte - pd.Timedelta(days=6)
        casos = (
            ceros.loc[ceros["fecha"].between(inicio, fecha_corte)]
            .groupby(["tienda_id", "producto_id"], as_index=False)["fecha"]
            .nunique()
            .rename(columns={"fecha": "dias_en_cero"})
        )
        casos = casos.loc[casos["dias_en_cero"].ge(2)].merge(
            productos, on="producto_id", how="left", validate="many_to_one"
        )
        casos["riesgo"] = (
            casos["dias_en_cero"]
            * (casos["rotacion_esperada"] / 7)
            * (casos["precio_lista"] - casos["costo"])
        )
        ventanas.append(casos[["tienda_id", "producto_id", "dias_en_cero", "riesgo"]])

    return pd.concat(ventanas, ignore_index=True)


def main() -> None:
    casos = calcular_riesgos()
    riesgo = casos["riesgo"]
    q1, q3 = riesgo.quantile([0.25, 0.75])
    iqr = q3 - q1
    limite_superior = q3 + 1.5 * iqr
    outliers_altos = riesgo.gt(limite_superior)

    percentiles = pd.Series(
        {percentil: riesgo.quantile(percentil / 100) for percentil in range(1, 101)},
        name="margen_potencial_en_riesgo",
    )
    p99 = percentiles.loc[99]

    plt.style.use("seaborn-v0_8-whitegrid")
    figura, ejes = plt.subplots(1, 2, figsize=(14, 5.5), constrained_layout=True)
    figura.suptitle(
        "Margen potencial en riesgo: percentiles y valores atipicos\n"
        "Ventanas moviles inclusivas de 7 dias; solo casos con 2 o mas dias en cero",
        fontsize=14,
        fontweight="bold",
    )

    ejes[0].plot(percentiles.index, percentiles.values, color="#0b5e9b", linewidth=2.5)
    for percentil in (25, 50, 75, 95, 99):
        valor = percentiles.loc[percentil]
        ejes[0].scatter(percentil, valor, color="#c6491b", zorder=3)
        ejes[0].annotate(
            f"P{percentil}: ${valor:,.2f}",
            (percentil, valor),
            textcoords="offset points",
            xytext=(4, 7),
            fontsize=8,
        )
    ejes[0].set_xlabel("Percentil")
    ejes[0].set_ylabel("Margen potencial en riesgo ($)")
    ejes[0].set_xlim(1, 100)
    ejes[0].set_title("Curva de percentiles")

    riesgo_visible = riesgo.loc[riesgo.le(p99)]
    ejes[1].hist(riesgo_visible, bins=55, color="#4c9e76", edgecolor="white")
    ejes[1].axvline(q1, color="#0b5e9b", linestyle="--", label=f"P25: ${q1:,.2f}")
    ejes[1].axvline(riesgo.median(), color="#0b5e9b", label=f"Mediana: ${riesgo.median():,.2f}")
    ejes[1].axvline(q3, color="#0b5e9b", linestyle="--", label=f"P75: ${q3:,.2f}")
    ejes[1].axvline(
        limite_superior,
        color="#c6491b",
        linewidth=2,
        label=f"Limite IQR: ${limite_superior:,.2f}",
    )
    ejes[1].set_xlabel("Margen potencial en riesgo ($), mostrado hasta P99")
    ejes[1].set_ylabel("Casos-ventana")
    ejes[1].set_title(
        f"Distribucion y outliers: {outliers_altos.sum():,} ({outliers_altos.mean():.2%})"
    )
    ejes[1].legend(fontsize=8)

    figura.savefig(OUTPUT_PATH, dpi=200, bbox_inches="tight")

    figura_box, eje_box = plt.subplots(figsize=(11, 4.5), constrained_layout=True)
    eje_box.boxplot(
        riesgo,
        vert=False,
        patch_artist=True,
        boxprops={"facecolor": "#b8d8e8", "edgecolor": "#0b5e9b"},
        medianprops={"color": "#c6491b", "linewidth": 2},
        whiskerprops={"color": "#0b5e9b"},
        capprops={"color": "#0b5e9b"},
        flierprops={"marker": ".", "markerfacecolor": "#c6491b", "markeredgecolor": "#c6491b", "alpha": 0.35},
    )
    eje_box.axvline(
        limite_superior,
        color="#c6491b",
        linestyle="--",
        label=f"Limite IQR: ${limite_superior:,.2f}",
    )
    eje_box.set_title(
        "Box plot del margen potencial en riesgo\n"
        f"{outliers_altos.sum():,} outliers altos ({outliers_altos.mean():.2%})"
    )
    eje_box.set_xlabel("Margen potencial en riesgo ($)")
    eje_box.set_yticks([])
    eje_box.legend(loc="upper right")
    figura_box.savefig(BOXPLOT_PATH, dpi=200, bbox_inches="tight")

    print(f"Grafica creada: {OUTPUT_PATH}")
    print(f"Box plot creado: {BOXPLOT_PATH}")
    print(f"Casos-ventana: {len(casos):,}")
    print(f"Limite superior IQR: ${limite_superior:,.2f}")
    print(f"Outliers altos: {outliers_altos.sum():,} ({outliers_altos.mean():.2%})")


if __name__ == "__main__":
    main()