from pathlib import Path

import matplotlib.pyplot as plt

from equipo_lib import cargar_variante, detectar_quiebres


DATA_DIR = Path(__file__).parent / "datos"
OUTPUT_PATH = Path(__file__).parent / "boxplot_costo_estimado_quiebres.png"
DIAS_MINIMOS_QUIEBRE = 2
VENTANA_QUIEBRES_DIAS = 7


def main() -> None:
    datos = cargar_variante(str(DATA_DIR))
    casos = detectar_quiebres(
        datos, DIAS_MINIMOS_QUIEBRE, VENTANA_QUIEBRES_DIAS
    )
    if casos.empty:
        print("No se generó el box plot: no hay casos con dos días en cero.")
        return

    costos = casos["costo_estimado"]
    q1, q3 = costos.quantile([0.25, 0.75])
    iqr = q3 - q1
    limite_superior = q3 + 1.5 * iqr
    outliers = casos.loc[
        costos.gt(limite_superior),
        ["tienda_id", "producto_id", "dias_cero", "costo_estimado"],
    ].sort_values("costo_estimado", ascending=False)

    plt.style.use("seaborn-v0_8-whitegrid")
    figura, eje = plt.subplots(figsize=(11, 4.5), constrained_layout=True)
    eje.boxplot(
        costos,
        vert=False,
        patch_artist=True,
        boxprops={"facecolor": "#b8d8e8", "edgecolor": "#0b5e9b"},
        medianprops={"color": "#c6491b", "linewidth": 2},
        whiskerprops={"color": "#0b5e9b"},
        capprops={"color": "#0b5e9b"},
        flierprops={"marker": "o", "markerfacecolor": "#c6491b", "markeredgecolor": "#c6491b"},
    )
    eje.axvline(q1, color="#0b5e9b", linestyle="--", label=f"P25: ${q1:,.0f}")
    eje.axvline(costos.median(), color="#c6491b", label=f"Mediana: ${costos.median():,.0f}")
    eje.axvline(q3, color="#0b5e9b", linestyle="--", label=f"P75: ${q3:,.0f}")
    eje.axvline(
        limite_superior,
        color="#7a4e00",
        linestyle=":",
        linewidth=2,
        label=f"Limite IQR: ${limite_superior:,.0f}",
    )
    eje.set_title(
        "Box plot del costo estimado de quiebre\n"
        "dias en cero x (rotacion semanal esperada / 7) x precio de lista"
    )
    eje.set_xlabel("Costo estimado ($)")
    eje.set_yticks([])
    eje.legend(loc="upper right")
    figura.savefig(OUTPUT_PATH, dpi=200, bbox_inches="tight")

    print(f"Gráfica creada: {OUTPUT_PATH}")
    print(f"Casos analizados: {len(casos):,}")
    print(f"P25: ${q1:,.2f}; mediana: ${costos.median():,.2f}; P75: ${q3:,.2f}")
    print(f"Límite superior IQR: ${limite_superior:,.2f}")
    print(f"Outliers altos: {len(outliers):,} ({len(outliers) / len(casos):.2%})")
    print("Mayores cinco casos:")
    print(outliers.head().to_string(index=False) if not outliers.empty else "Ninguno")


if __name__ == "__main__":
    main()