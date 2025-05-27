import pandas as pd
from tabulate import tabulate

class DataImporter:
    def __init__(self):
        self.__path_excel = None
        self.__path_csv = None
        self.__df = None
        self.__sheet = None
        self.__nombre_columna_formato = None
        self.__titus_cols = None
        self.__df_revisar_dup = None
        self.__path_parquet = None

    def importar_excel(self, path, sheet):
        self.__path_excel = path
        self.__sheet = sheet
        try:
            self.__df = pd.read_excel(self.__path_excel, sheet_name=self.__sheet)
        except Exception as e:
            print(f" Error al cargar el excel: {e}")

    def get_df(self):
        if  self.__df is not None:
            return self.__df
        else:
            print("No se puede retornar el df porque no existe")

    def set_df(self, df):
        if df is not None:
            self.__df = df
        else: raise ValueError("No existe el df a setear")

    # Las funciones de importacion reciben todos los datos en str, si se quiere otro formato de datos se debe modificar con las funciones para cada caso
    def importar_csv_pcoma(self, path_csv):
        self.__path_csv = path_csv
        try:
            self.__df = pd.read_csv(self.__path_csv, sep=";", on_bad_lines="skip", dtype=str, encoding='utf-8')
        except Exception as e:
            print(f" Error al cargar el csv: {e}")

    def importar_csv_tab(self, path_csv):
        self.__path_csv = path_csv
        try:
            self.__df = pd.read_csv(self.__path_csv, sep="\t", on_bad_lines="skip", dtype=str, encoding='utf-8')
        except Exception as e:
            print(f" Error al cargar el csv: {e}")

    def importar_csv_coma(self, path_csv):
        self.__path_csv = path_csv
        try:
            self.__df = pd.read_csv(self.__path_csv, sep=",", on_bad_lines="skip", dtype=str, encoding='utf-8')
        except Exception as e:
            print(f" Error al cargar el csv: {e}")

    def imprimir_titulos_df(self):
        self.__titus_cols = self.__df.columns
        print(self.__titus_cols)

    def imprimir_datos_df(self):
        if self.__df is not None:
            print("Columnas: ")
            self.__titus_cols = self.__df.columns
            print(self.__titus_cols)
            print("Head 10")
            print(tabulate(self.__df.head(10), headers="keys", tablefmt="fancy_grid") )
            print("Tail 10")
            print(tabulate(self.__df.tail(10), headers="keys", tablefmt="fancy_grid"))
            #dtypes_dict = self.__df.dtypes.to_dict()
            # Imprimir usando tabulate
            #print(tabulate(dtypes_dict.items(), headers=["Columna", "Tipo de Datos"], tablefmt="fancy_grid"))
        else:
            print("No hay df cargado")

    def definir_datos_tipo_float_en_columna(self, nombre_columna):
        self.__nombre_columna_formato = nombre_columna
        if self.__df is not None:
            if nombre_columna in self.__df.columns:
                # Verificamos si hay comas o puntos en los datos
                if self.__df[nombre_columna].astype(str).str.contains(",", regex=False).any() and self.__df[nombre_columna].astype(str).str.contains(".", regex=False).any():
                    # Reemplazamos las comas por punto si ambos están presentes
                    self.__df[nombre_columna] = self.__df[nombre_columna].replace({',': ""}, regex=True)
                    self.__df[nombre_columna] = pd.to_numeric(self.__df[nombre_columna], errors='coerce')
                    #print(f"Comas reemplazadas y convertidas a tipo float en columna {nombre_columna}")

                # Caso donde solo hay comas
                elif self.__df[nombre_columna].astype(str).str.contains(",").any():
                    #print(f"Formateando columna {nombre_columna} en tipo float y eliminando comas")
                    # Reemplazamos las comas por punto para convertir a float
                    self.__df[nombre_columna] = self.__df[nombre_columna].replace({',': '.'}, regex=True)
                    # Convertimos a float con manejo de errores
                    self.__df[nombre_columna] = pd.to_numeric(self.__df[nombre_columna], errors='coerce')
                    #print(f"Formato definido exitosamente para {nombre_columna}")

                # Caso donde no hay comas
                else:
                    self.__df[nombre_columna] = pd.to_numeric(self.__df[nombre_columna], errors='coerce')
                    #print(f"No se encontraron comas en la columna {nombre_columna}, pero se ha convertido a float")

            else:
                print(f"La columna {nombre_columna} no existe en el DataFrame.")
        else:
            print("No se tiene un DataFrame cargado")


    def definir_datos_tipo_int_en_columna(self, nombre_columna):
        self.__nombre_columna_formato = nombre_columna
        if self.__df is not None:
            if nombre_columna in self.__df.columns:
                if self.__df[nombre_columna].astype(str).str.contains(",", regex=False).any() or self.__df[nombre_columna].astype(str).str.contains(".", regex=False).any():
                    valores_con_problema = self.__df[nombre_columna][
                        self.__df[nombre_columna].astype(str).str.contains(",") |
                        self.__df[nombre_columna].astype(str).str.contains(".")
                        ].unique()  # Obtener valores únicos

                    # Mostrar mensaje con los valores que tienen punto o coma
                    #print(f"No se puede convertir la columna '{nombre_columna}' a entero porque contiene punto o coma.")
                    #print(f"Valores con problema en '{nombre_columna}': {valores_con_problema}")

                    # Validacion de que no exista punto ni coma para asegurar que los datos son int
                    #print(f"No se puede convertir la columna {nombre_columna} en entero porque contiene punto o coma")
                else:
                    self.__df[nombre_columna] = self.__df[nombre_columna].astype(int)
                    #print("Columna convertida a formato int exitosamente")
            else:
                print("La columna no existe en el df")
        else:
            print("No se tiene un df cargado")

    def cambiar_nombre_col(self, col, nombre_nuevo):
        if col in self.__titus_cols:
            print("Nombre encontrado, cambiando el nombre de la columna")
            self.__df.rename(columns={col: nombre_nuevo}, inplace=True)
            self.__titus_cols = self.__df.columns
            print("Nombre de columna cambiado.")
            print(self.__titus_cols)
        else:
            print("El nombre de la columna no existe")

    def definir_datos_tipo_fecha_año_mes_dia(self, nombre_columna):
        # Recibe datos str del df, los convierte en el formato inicial que recibe año-mes-día y los pone en el formato fecha deseado mes/día/año
        try:
            self.__df[nombre_columna] = pd.to_datetime(self.__df[nombre_columna], format="%Y-%m-%d")
            #print("Columna convertida a fecha exitosamente")
            self.__df[nombre_columna] = self.__df[nombre_columna].dt.strftime("%m/%d/%Y")
        except Exception as e:
            print(f"Error al procesar la columna '{nombre_columna}': {e}")

    def definir_datos_tipo_fecha_mes_dia_año(self, nombre_columna):
        # Recibe datos str del df, los convierte en el formato inicial que recibe mes/día/año
        try:
            self.__df[nombre_columna] = pd.to_datetime(self.__df[nombre_columna], format="mixed", dayfirst=False)
            #print("Columna convertida a fecha exitosamente")
        except Exception as e:
            print(f"Error al procesar la columna '{nombre_columna}': {e}")

    def revisar_info_sin_duplicados(self, col):
        # Funcion usada para visualizar que esten bien las fechas
        self.__df_revisar_dup = self.__df[col].copy()
        self.__df_revisar_dup = self.__df_revisar_dup.drop_duplicates()
        print(self.__df_revisar_dup)

    def importar_parquet(self, path_parquet):
        self.__path_parquet = path_parquet
        try:
            self.__df = pd.read_parquet(self.__path_parquet)
            print("Archivo Parquet importado exitosamente")
        except Exception as e:
            p