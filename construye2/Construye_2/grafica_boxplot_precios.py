from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


DATA_PATH = Path(__file__).parent / "datos" / "productos.csv"
OUTPUT_PATH = Path(__file__).parent / "boxplot_precios_productos.png"


def main() -> None:
    productos = pd.read_csv(DATA_PATH)
    precios = pd.to_numeric(productos["precio_lista"], errors="raise")

    q1, q3 = precios.quantile([0.25, 0.75])
    iqr = q3 - q1
    limite_inferior = q1 - 1.5 * iqr
    limite_superior = q3 + 1.5 * iqr
    outliers = productos.loc[
        precios.lt(limite_inferior) | precios.gt(limite_superior),
        ["producto_id", "precio_lista"],
    ].sort_values("precio_lista")

    plt.style.use("seaborn-v0_8-whitegrid")
    figura, eje = plt.subplots(figsize=(11, 4.5), constrained_layout=True)
    eje.boxplot(
        precios,
        vert=False,
        patch_artist=True,
        boxprops={"facecolor": "#b8d8e8", "edgecolor": "#0b5e9b"},
        medianprops={"color": "#c6491b", "linewidth": 2},
        whiskerprops={"color": "#0b5e9b"},
        capprops={"color": "#0b5e9b"},
        flierprops={"marker": "o", "markerfacecolor": "#c6491b", "markeredgecolor": "#c6491b"},
    )
    eje.axvline(q1, color="#0b5e9b", linestyle="--", label=f"P25: ${q1:,.2f}")
    eje.axvline(precios.median(), color="#c6491b", label=f"Mediana: ${precios.median():,.2f}")
    eje.axvline(q3, color="#0b5e9b", linestyle="--", label=f"P75: ${q3:,.2f}")
    eje.axvline(
        limite_superior,
        color="#7a4e00",
        linestyle=":",
        linewidth=2,
        label=f"Limite IQR: ${limite_superior:,.2f}",
    )
    eje.set_title(
        "Box plot de precios de lista de productos\n"
        f"{len(outliers)} productos con precio atipico segun IQR"
    )
    eje.set_xlabel("Precio de lista ($)")
    eje.set_yticks([])
    eje.legend(loc="upper right")
    figura.savefig(OUTPUT_PATH, dpi=200, bbox_inches="tight")

    print(f"Grafica creada: {OUTPUT_PATH}")
    print(f"Productos: {len(productos):,}")
    print(f"P25: ${q1:,.2f}; mediana: ${precios.median():,.2f}; P75: ${q3:,.2f}")
    print(f"Limites IQR: ${limite_inferior:,.2f} a ${limite_superior:,.2f}")
    print("Productos atipicos:")
    print(outliers.to_string(index=False) if not outliers.empty else "Ninguno")


if __name__ == "__main__":
    main()