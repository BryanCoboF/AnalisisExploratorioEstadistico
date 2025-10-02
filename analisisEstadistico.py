import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import os
from tabulate import tabulate
from mpl_toolkits.mplot3d import Axes3D
from sklearn.preprocessing import LabelEncoder
import plotly.express as px
from sklearn.preprocessing import MinMaxScaler



class AnalisisEstadistico:
    def __init__(self):
        self.df = None


    def cargar_datos(self, ruta_archivo: str, hoja: str = "Sheet1"):
        if not os.path.exists(ruta_archivo):
            raise FileNotFoundError(f"Archivo no encontrado en: {ruta_archivo}")

        df = pd.read_excel(ruta_archivo, sheet_name=hoja)

        # Identificar columnas categóricas y convertir a dummies
        cat_cols = df.select_dtypes(include=['object']).columns
        df_encoded = pd.get_dummies(df, columns=cat_cols, drop_first=True)

        self.df = df_encoded
        print(f"Datos cargados correctamente desde: {ruta_archivo}")
        print(f"Dimensiones del DataFrame: {self.df.shape}")
        print(tabulate(df_encoded.head(5), headers="keys", tablefmt="fancy_grid"))


    def __analisis_descriptivo(self):
        print("\n📊 Resumen estadístico:")
        print(self.df.describe())

    def __matriz_correlacion(self):
        print("\n📈 Matriz de correlación:")
        corr_matrix = self.df.corr()
        print(corr_matrix)

        # Calcular tamaño dinámico
        cols = corr_matrix.shape[1]
        size = max(10, cols * 0.8)

        # Crear el heatmap
        plt.figure(figsize=(size, size))
        sns.heatmap(
            corr_matrix,
            annot=True,
            cmap="coolwarm",
            fmt=".2f",
            square=True,
            linewidths=0.5,
            cbar_kws={"shrink": 0.8}
        )
        plt.title("Matriz de Correlación", fontsize=16)
        plt.xticks(rotation=45, ha='right')
        plt.yticks(rotation=0)
        plt.tight_layout()

        # Mostrar y guardar
        plt.savefig("matriz_correlacion.png", dpi=300)
        plt.show()
        print("📁 Matriz de correlación guardada como 'matriz_correlacion.png'")

    def __normalizar_datos(self):
        print("\n🔧 Normalizando datos numéricos...")
        scaler = MinMaxScaler()
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        self.df[numeric_cols] = scaler.fit_transform(self.df[numeric_cols])
        print("✅ Datos normalizados con Min-Max Scaling.")

    def __distribucion_conjunta(self):
        print("\n📉 Distribución conjunta de las variables más correlacionadas:")
        corr = self.df.corr().abs()
        np.fill_diagonal(corr.values, 0)
        var1, var2 = corr.unstack().idxmax()

        sns.jointplot(data=self.df, x=var1, y=var2, kind="kde", fill=True)
        plt.suptitle(f"Distribución conjunta: {var1} vs {var2}", y=1.02)
        plt.show()

    def ejecutar_analisis(self):
        if self.df is None:
            raise ValueError("Primero debes cargar los datos con el método `cargar_datos`.")
        self.__normalizar_datos()
        self.__analisis_descriptivo()
        self.__matriz_correlacion()
        #self.__distribucion_conjunta()
        self.graficar_3d("Patrimonio", "Average of INGRESOS", "Probabilidad Mora 0D")
        self.graficar_3d("Patrimonio", "Average of EGRESOS", "Probabilidad Mora 0D")
        self.graficar_5d("Patrimonio", "Average of EGRESOS", "Probabilidad Mora 0D", "TIPO (E-N-V-F)_Original", "TIPO (E-N-V-F)_Reestructurada")
        self.graficar_5d("Patrimonio", "Average of EGRESOS", "Probabilidad Mora 0D", "GARANTÍA_GQ", "GARANTÍA_GR")




    def graficar_3d(self, x_col: str, y_col: str, z_col: str):
        if self.df is None:
            raise ValueError("Primero debes cargar los datos.")

        if not all(col in self.df.columns for col in [x_col, y_col, z_col]):
            raise ValueError("Una o más columnas no existen en el DataFrame.")

        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, projection='3d')

        ax.scatter(self.df[x_col], self.df[y_col], self.df[z_col], c='dodgerblue', alpha=0.7, edgecolor='k')

        ax.set_xlabel(x_col)
        ax.set_ylabel(y_col)
        ax.set_zlabel(z_col)
        ax.set_title(f"Gráfico 3D: {x_col} vs {y_col} vs {z_col}")

        plt.tight_layout()
        plt.show()

    def graficar_5d(self, x_col, y_col, z_col, color_col, size_col):
        if self.df is None:
            raise ValueError("Primero debes cargar los datos.")

        for col in [x_col, y_col, z_col, color_col, size_col]:
            if col not in self.df.columns:
                raise ValueError(f"La columna '{col}' no existe en el DataFrame.")

        # Convertir booleanos a numéricos si es necesario
        df_plot = self.df.copy()
        for col in [color_col, size_col]:
            if df_plot[col].dtype == bool:
                df_plot[col] = df_plot[col].astype(int)

        # Normalizar tamaño
        size = df_plot[size_col]
        size_scaled = 50 * (size - size.min()) / (size.max() - size.min()) + 10

        # Crear figura 3D
        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, projection='3d')

        p = ax.scatter(
            df_plot[x_col],
            df_plot[y_col],
            df_plot[z_col],
            c=df_plot[color_col],
            s=size_scaled,
            cmap="plasma",
            alpha=0.8,
            edgecolor='k'
        )

        ax.set_xlabel(x_col)
        ax.set_ylabel(y_col)
        ax.set_zlabel(z_col)
        ax.set_title(f"Gráfico 5D: {x_col}, {y_col}, {z_col}, color={color_col}, size={size_col}")

        # Agregar barra de color
        cbar = plt.colorbar(p, ax=ax, shrink=0.6)
        cbar.set_label(color_col)

        plt.tight_layout()
        plt.show()

    def graficar_7d(self, x, y, z, color, size, symbol, animation):
        """
        Visualización en 7 dimensiones usando plotly:
        - 3D: x, y, z
        - Color: color
        - Tamaño: size
        - Símbolo: symbol
        - Animación: animation
        """
        import plotly.express as px
        from sklearn.preprocessing import LabelEncoder

        df = self.df.copy()

        # Convertir categóricas a numéricas si es necesario
        label_encoders = {}
        for col in [color, size, symbol, animation]:
            if df[col].dtype == 'object' or df[col].dtype.name == 'category' or df[col].dtype == bool:
                le = LabelEncoder()
                df[col] = le.fit_transform(df[col].astype(str))
                label_encoders[col] = le

        # Crear gráfica interactiva
        fig = px.scatter_3d(
            df,
            x=x,
            y=y,
            z=z,
            color=color,
            size=size,
            symbol=symbol,
            animation_frame=animation,
            opacity=0.7,
            height=800,
            width=1000
        )

        fig.update_layout(
            title="Visualización en 7 dimensiones (3D + color + tamaño + símbolo + animación)",
            margin=dict(l=0, r=0, t=50, b=0)
        )
        fig.show()


# -------------------------------
# USO DEL SCRIPT
# -------------------------------

if __name__ == "__main__":
    #ruta = r"D:\SUMAK KAWSAY\DESARROLLOS Y ANÁLISIS\CRÉDITO\ANÁLISIS\Muestreo Probabilidad de Mora\Analizar.xlsx"
    #ruta = r"D:\SUMAK KAWSAY\DESARROLLOS Y ANÁLISIS\CRÉDITO\ANÁLISIS\Muestreo Probabilidad de Mora\AnalizarProb2.xlsx"
    ruta = r"D:\SUMAK KAWSAY\DESARROLLOS Y ANÁLISIS\CRÉDITO\ANÁLISIS\Muestreo Probabilidad de Mora\AnalizarProbOpe.xlsx"

    analisis = AnalisisEstadistico()
    analisis.cargar_datos(ruta_archivo=ruta)
    analisis.ejecutar_analisis()
