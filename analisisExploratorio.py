import matplotlib.pyplot as plt
import pandas as pd
import data_importer as di
from tkinter import Tk, filedialog
import numpy as np
from tabulate import tabulate
import seaborn as sns


class AnalisisExploratorio:
    def __init__(self):
        self.__df = None
        self.__info_cardinalidad = None

    def set_df(self, df):
        if df is not None:
            self.__df = df
        else: raise ValueError("El df no existe no se puede setear")

    def get_df(self):
        if self.__df is not None:
            return self.__df
        else: raise ValueError("El df no existe no se puede retornar")

    def ejecutar_analisis_exploratorio_completo(self):
        self.__importar_data_excel()
        self.__imprimir_datos()
        self.__cardinalidad()
        self.__estadisticas_descriptivas()
        self.__analisis_distribucion_numericas()
        self.__matriz_correlacion()

    def ejecutar_analisis_correlacion(self):
        self.__importar_data_excel()
        self.__cardinalidad()
        self.__estadisticas_descriptivas()
        self.__matriz_correlacion()

    def ejecutar_analisis_volatilidad(self):
        self.__importar_data_excel()
        self.__cardinalidad()
        self.__estadisticas_descriptivas()
        self.__volatilidad()



    def __importar_data_excel(self):
        root = Tk()  # Incializa la ventana de selección de archivos.
        root.withdraw()  # Oculta la ventana principal de Tkinter
        # Abre el cuadro de diálogo para seleccionar el archivo
        file_path = filedialog.askopenfilename(title="Selecciona un archivo Excel",
                                               filetypes=[("Archivos Excel", "*.xlsx;*.xls")])
        if not file_path:
            print("No se seleccionó ningún archivo")
            return
        try:
            data_imp = di.DataImporter()
            data_imp.importar_excel(file_path, "Sheet1")
            self.set_df(data_imp.get_df())
        except Exception as e:
            print(f"No se puede importar el archivo exscel {str(e)}")


    def __estadisticas_descriptivas(self, include_objects=False):
        if self.__df is None:
            print("No existe el df no se puede obtener estadísticas")
            return

        print(" ----- Estadísticas descriptivas del df ---------")

        if include_objects:
            print(self.__df.describe(include="all").T)
        else:
            print(self.__df.describe().T)

    def __imprimir_datos(self):
        if self.__df is None:
            print("No existe el df no se puede imprimir datos")
            return
        print(tabulate(self.__df.head(5), tablefmt="fancy_grid", headers="keys"))
        print(tabulate(self.__df.tail(5), tablefmt="fancy_grid", headers="keys"))



    def __cardinalidad(self, umbral=20):
        if self.__df is None:
            print("No existe el df no se puede obtener cardinalidad")
            return
        print(" --------- Análisis de Cardinalidad --------")
        self.__info_cardinalidad = pd.DataFrame({"Tipo dato": self.__df.dtypes,
                                                 "Valores únicos": self.__df.nunique(),
                                                 "Porcentaje Único (%)": (self.__df.nunique() / len(self.__df))*100
                                                 })

        print(self.__info_cardinalidad.sort_values(by="Valores únicos", ascending=False))
        print(f"Columnas con alta cardinalidad (más de {umbral} valores únicos: ", self.__info_cardinalidad[self.__info_cardinalidad["Valores únicos"] > umbral].index.tolist())
        print(f"Columnas con baja cardinalidad (más de {umbral} valores únicos: ", self.__info_cardinalidad[self.__info_cardinalidad["Valores únicos"] <= umbral].index.tolist())


    def __identificar_tipos_datos(self):
        if self.__df is None:
            print("No existe el df no se puede obtener tipos de datos")
            return
        print(" ----- Indentificación de Tipos de datos ---------")

        print("\nTipos de datos originales")
        tipos_datos = self.__df.dtypes
        print(tipos_datos)


        for col, dtype in tipos_datos:
            if pd.api.types.is_numeric_dtype(dtype):
                print(f" - {col}: Numérica")
            elif pd.api.types.is_object_dtype(dtype) or pd.api.types.is_string_dtype(dtype):
                conteo_valores_unicos = self.__df[col].nunique()
                num_filas = len(self.__df)
                if conteo_valores_unicos / num_filas < 0.05 and conteo_valores_unicos <=50:
                    print(f" {col}: Categórica (discreta, {conteo_valores_unicos}")
                else:
                    print(f"{col}: Texto/Categórica (alta cardinalidad)")
            elif pd.api.types.is_datetime64_any_dtype(dtype):
                    print(f"{col}: Tipo fecha")
            elif pd.api.types.is_bool_dtype(dtype):
                print(f"{col}: bool")
            else: print(f"{col}: Otro tipo {dtype}")



    def __analisis_distribucion_numericas(self, columna=None):
        if self.__df is None:
            print("No existe el df no se puede obtener las distribuciones")
            return
        print(" ------Obteniendo Distribuciones ----")
        cols_numericas = self.__df.select_dtypes(include=np.number).columns

        if columna:
            if columna in cols_numericas:
                cols_grafica = [columna]
            else:
                print(f"Columna {columna} no numérica o no existe")
                return
        else:
            cols_grafica = cols_numericas.tolist()


        if len(cols_grafica) == 0:
            print(f" No existen columnas para graficar distribución")
            return




        for col in cols_grafica:
            print(f"\n--- Distribución de la columna '{col}' (Numérica) ---")
            print(self.__df[col].describe())

            prom = self.__df[col].mean()
            std_err = self.__df[col].std() / np.sqrt(len(self.__df[col].dropna()))
            std = self.__df[col].std()
            moda = self.__df[col].mode()[0]


            intervalo_sup = prom + 1.96*std
            intervalo_inf = prom - 1.96*std

            plt.figure(figsize=(10,6))
            sns.histplot(self.__df[col].dropna(), kde=True, bins=30)
            plt.axvline(prom, color="red", linestyle="--", label=f"Promedio: {prom:.2f}")
            plt.axvline(moda, color="green", linestyle="--", label=f"Moda: {moda:.2f}")
            plt.axvline(intervalo_sup, color="blue", linestyle="--", label=f"Lim sup: {intervalo_sup:.2f}")
            plt.axvline(intervalo_inf, color="blue", linestyle="--", label=f"Lim sup: {intervalo_inf:.2f}")
            plt.title(f"Distribución de {col}")
            plt.xlabel(col)
            plt.ylabel("Frecuencias")
            plt.legend()
            plt.grid(axis="y", alpha=0.75)
            plt.show()
        else:
            print(f"{col} no es numérica o no existe no se puede graficar el histograma")


    def __matriz_correlacion(self):
        if self.__df is None:
            print("No existe el df no se puede obtener la matriz de correlación")
            return

        df_numerico = self.__df.select_dtypes(include=np.number)

        if df_numerico.empty:
            print("El df no tiene columnas numéricas no se puede obtener la correlacion")
            return

        matriz_correlacion = df_numerico.corr(method="pearson")

        n_vars = len(matriz_correlacion.columns)
        fig_size = max(10, n_vars*0.6)

        plt.figure(figsize=(fig_size, fig_size))
        sns.heatmap(matriz_correlacion, annot=True, cmap="coolwarm", fmt=".2f", linewidths=0.5, cbar=True, annot_kws={"size": 8})
        plt.xticks(rotation=45, ha="right",fontsize=8)
        plt.yticks(rotation=0, fontsize=8)
        plt.title("Matriz Correlación", fontsize=10)
        plt.tight_layout()
        plt.show()


    def __variacion_porcencual_fecha(self, nombre_col_fecha):
        if self.__df is None:
            print("No existe el df no se puede obtener la volatilidad")
            return

        if nombre_col_fecha not in self.__df.columns:
            print("No se tiene una columna fecha corte, no se puede calcular la variación de los indicadores")
            return

        self.__df[nombre_col_fecha] = self.__df.sort_values(by=nombre_col_fecha)

        fechas = self.__df[nombre_col_fecha].iloc[1:].reset_index(drop=True)

        df_numerico = self.__df.select_dtypes(include=[np.number])

        if df_numerico.empty:
            print("El df no tiene columnas numéricas no se puede obtener la volatilidad")
            return


        retornos = df_numerico.pct_change().replace([np.inf, -np.inf], np.nan).dropna()  # Calculando los retornos evitando división por cero
        retornos[nombre_col_fecha] = fechas

        


        volatilidad = retornos.std()
        print("****** Retornos ******")
        print(tabulate(retornos, headers="keys", tablefmt="fancy_grid"))

        print("---- Volatilidad-------")
        print(volatilidad)


if __name__ == '__main__':
    analizador = AnalisisExploratorio()
    #analizador.ejecutar_analisis_exploratorio()
    #analizador.ejecutar_analisis_correlacion()
    analizador.ejecutar_analisis_volatilidad()



