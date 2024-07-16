import streamlit as st
import pandas as pd
import plotly.express as px
import pyarrow as pa
import pyarrow.parquet as pq

st.set_page_config(
    layout="wide",
)

def print_rating_table(rating_file_path):
	df_schema = pa.schema([("rank_num", "int32"),
		("shooters_name", "string"), 
		("rating", pa.float32()),
		("class", "string"),
		("class_avg", pa.decimal128(38,9)),
		("matches", "int32"),
		("percents", pa.list_(pa.float32())), 
		("places", pa.list_(pa.int32()))])
	rating_df = pd.read_parquet(rating_file_path, schema=df_schema)
	rating_df = rating_df.sort_values(by=['rank_num']).round(2).set_index(rating_df.columns[0]).rename(columns={'rank_num': 'Номер у рейтингу', 'shooters_name': 'Ім\'я спортсмена', 'rating': 'Рейтинг', 'class': 'Клас спортсмена','class_avg':'Середній результат','matches':'Кількість матчів'})
	
	st.data_editor(
	    rating_df,
	    column_config={
	        "percents": st.column_config.BarChartColumn(
	            "Останні 6 змаганнь",
	            help="Відсотки від 1го місця",
	            y_min=0,
	            y_max=1,
	        ),
	        "places": st.column_config.ListColumn(
	            "Зайняті місця",
	            width="medium",
	        )
	        #"places": "Зайняті місця"
	    },
	    hide_index=False,
	    key = rating_file_path
	)

file_path = "https://storage.googleapis.com/alphastats_ratings/rating_carabin_1_20240707.csv"
extended_path = "https://storage.googleapis.com/alphastats_ratings/extended_rating_1.parquet"
extended_path_SAS = "https://storage.googleapis.com/alphastats_ratings/extended_rating_1_SAS.parquet"
extended_path_Lady = "https://storage.googleapis.com/alphastats_ratings/extended_rating_1_lady.parquet"
extended_path_Senior = "https://storage.googleapis.com/alphastats_ratings/extended_rating_1_senior.parquet"
extended_path_Junior = "https://storage.googleapis.com/alphastats_ratings/extended_rating_1_junior.parquet"

st.title("Рейтинг спортсменів-стрільців. Практична стрільба. Карабін.")
st.write("Останне оновлення рейтингу 2024.07.07")
st.write("Таблиця рейтингів* та классів**")
print_rating_table(extended_path)


df = pd.read_csv(file_path,
                 sep=",")
df_sorted = df.sort_values(by=['rank_num']).round(2).set_index(df.columns[0])
df_formated = df_sorted.rename(columns={'rank_num': 'Номер у рейтингу', 'shooters_name': 'Ім\'я спортсмена', 'rating': 'Рейтинг', 'class': 'Клас спортсмена','class_avg':'Середній результат','matches':'Кількість матчів'})
fig = px.histogram(df_formated, x="Рейтинг")
st.write(fig)

fig2 = px.histogram(df_formated, x="Клас спортсмена")
st.write(fig2)

st.write("* для розрахунку рейтингу використовуються данні з останніх 6 матчів національного рівня (Чемпіонат України, Кубок України). Якщо спортсмен пропустив матч, то за такий матч спортсмен отримує свій найгірший результат помножений на 0.75. Далі результати за останні 6 матчів перемножуються на наступні коєфіцієнти: 1.0, 0.9, 0.8, 0.7, 0.6, 0.5, тачим чином, що б матчі, які видбулись останніми, мали вищу вагу. Сума результатів і є рейтингом спортсмена. Максимальний теоретично можливий тейтинг складає 450 балів (потрібно виграти 6 останніх матчів).")
st.write("** для розрахунку класса використовуються відсотки набрані спортсменом у останніх 6 матчах. З них беруться два найкращіх результата і обраховуєтся цередне значення цих двох найкращіх. Далі, відповідно до результатів вихначаються відповідні класи: Grand Master - 95-100%, Master - 85-94.9%, A - 75-84.9%, B - 60-74.9%, C - 40-59.9%, D - 2-39.9%")


st.title("SAS")
print_rating_table(extended_path_SAS)

st.title("Lady")
print_rating_table(extended_path_Lady)

st.title("Senior")
print_rating_table(extended_path_Senior)

st.title("Junior")
print_rating_table(extended_path_Junior)
