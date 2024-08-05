import streamlit as st
import pandas as pd
import plotly.express as px
import pyarrow as pa
import pyarrow.parquet as pq

st.set_page_config(page_title="Alpha Stats", layout="wide")

df_schema = pa.schema([("rank_num", "int32"),
	("progress", "string"), 
	("shooters_name", "string"), 
	("rating", pa.float32()),
	("class", "string"),
	("class_avg", pa.decimal128(38,9)),
	("matches", "int32"),
	("percents", pa.list_(pa.float32())), 
	("places", pa.list_(pa.int32()))])

def print_rating_table(rating_file_path):
	rating_df = pd.read_parquet(rating_file_path, schema=df_schema)
	rating_df = rating_df.sort_values(by=['rank_num']).round(2).set_index(rating_df.columns[0]).rename(columns={'rank_num': 'Номер у рейтингу', 'rating': 'Рейтинг', 'class': 'Клас спортсмена','class_avg':'Середній результат','matches':'Кількість матчів'})
	
	rating_df_column_config = {
	    "percents": st.column_config.BarChartColumn(
	        "Останні 6 змаганнь",
            help="Відсотки від 1го місця",
	        y_min=0,
	        y_max=1,
	    ),
	    "places": st.column_config.ListColumn(
	        "Зайняті місця",
	        width="medium",
	    ),
	    'shooters_name': 'Ім\'я спортсмена',
	    "progress": "Прогрес",
	    "rank_num": "Місце"
	}

	event = st.dataframe(
    	rating_df,
    	column_config=rating_df_column_config,
    	use_container_width=False,
    	hide_index=False,
    	on_select="rerun",
    	selection_mode="multi-row",
    	key = rating_file_path
	)

	filtered_df_column_config = {
	    "percents": st.column_config.ListColumn(
	        "Останні 6 змаганнь",
            help="Відсотки від 1го місця",
	    ),
	    "places": st.column_config.ListColumn(
	        "Зайняті місця",
	        width="medium",
	    ),
	    'shooters_name': 'Ім\'я спортсмена',
	    "rank_num": "Місце"
	}

	people = event.selection.rows
	filtered_df = rating_df.iloc[people]

	if filtered_df.size > 0:
		st.dataframe(filtered_df[['shooters_name','percents','places']],column_config=filtered_df_column_config)
		df = pd.DataFrame(filtered_df['percents'].values.tolist(), index=filtered_df['shooters_name']).add_prefix('percent')
		df = df.reset_index()
		df = df.reset_index()

		df_matches = pd.read_csv(file_path_matches,sep=",")
		res_df0 = df_matches.iloc[[0]].join(df[['shooters_name','percent0']], how='cross')
		res_df1 = df_matches.iloc[[1]].join(df[['shooters_name','percent1']].rename(columns={'percent1': 'percent0'}), how='cross')
		res_df2 = df_matches.iloc[[2]].join(df[['shooters_name','percent2']].rename(columns={'percent2': 'percent0'}), how='cross')
		res_df3 = df_matches.iloc[[3]].join(df[['shooters_name','percent3']].rename(columns={'percent3': 'percent0'}), how='cross')
		res_df4 = df_matches.iloc[[4]].join(df[['shooters_name','percent4']].rename(columns={'percent4': 'percent0'}), how='cross')
		res_df5 = df_matches.iloc[[5]].join(df[['shooters_name','percent5']].rename(columns={'percent5': 'percent0'}), how='cross')
		res_df = pd.concat([res_df0,res_df1,res_df2,res_df3,res_df4,res_df5])
		st.line_chart(res_df, x='match_date', y=['percent0'], color='shooters_name')

extended_path = "https://storage.googleapis.com/alphastats_ratings/2/extended_rating_v4.parquet"
extended_path_SAS = "https://storage.googleapis.com/alphastats_ratings/2/extended_rating_SAS_v2.parquet"
extended_path_SAO = "https://storage.googleapis.com/alphastats_ratings/2/extended_rating_SAO_v2.parquet"
extended_path_Lady = "https://storage.googleapis.com/alphastats_ratings/2/extended_rating_lady_v2.parquet"
extended_path_Senior = "https://storage.googleapis.com/alphastats_ratings/2/extended_rating_senior_v2.parquet"
extended_path_Junior = "https://storage.googleapis.com/alphastats_ratings/2/extended_rating_junior_v2.parquet"
file_path_matches = "https://storage.googleapis.com/alphastats_ratings/2/last6m.csv"

st.title("Рейтинг спортсменів-стрільців. Практична стрільба. Карабін.")
st.write("Останне оновлення рейтингу 2024.08.04")
st.write("Таблиця рейтингів* та классів**")
print_rating_table(extended_path)


df = pd.read_parquet(extended_path, schema=df_schema).sort_values(by=['class_avg'])
fig = px.histogram(df, x="rating")
fig2 = px.histogram(df, x="class")
st.write(fig)
st.write(fig2)

st.write("* для розрахунку рейтингу використовуються данні з останніх 6 матчів національного рівня (Чемпіонат України, Кубок України). Якщо спортсмен пропустив матч, то за такий матч спортсмен отримує свій середній результат помножений на 0.75. Далі результати за останні 6 матчів перемножуються на наступні коєфіцієнти: 1.0, 0.9, 0.8, 0.7, 0.6, 0.5, тачим чином, що б матчі, які видбулись останніми, мали вищу вагу. Сума результатів і є рейтингом спортсмена. Максимальний теоретично можливий тейтинг складає 450 балів (потрібно виграти 6 останніх матчів).")
st.write("** для розрахунку класса використовуються відсотки набрані спортсменом у останніх 6 матчах. З них беруться два найкращіх результата і обраховуєтся цередне значення цих двох найкращіх. Далі, відповідно до результатів вихначаються відповідні класи: Grand Master - 95-100%, Master - 85-94.9%, A - 75-84.9%, B - 60-74.9%, C - 40-59.9%, D - 2-39.9%")

st.title("SAO")
print_rating_table(extended_path_SAO)

st.title("SAS")
print_rating_table(extended_path_SAS)

st.title("Lady")
print_rating_table(extended_path_Lady)

st.title("Senior")
print_rating_table(extended_path_Senior)

st.title("Junior")
print_rating_table(extended_path_Junior)

st.title("Матчі враховані у рейтинг")
df_matches = pd.read_csv(file_path_matches,sep=",")
st.data_editor(
	df_matches,
	column_config={
		"num":"Номер",
		"name":"Назва",
		"match_date":"Дата",
		"results_link": st.column_config.LinkColumn(
            "Посилання на результати",
            help="Посилання на Practiscore результати",
            display_text="Перейти до результатів"
        )
	},
	hide_index=True,
	key = "matches"
)

st.write("*** підчас Кубку України 3 етап 2024, понижуючий коефіцієнт 0.75 не застосовувався для деяких спортсменів вимушено пропустивших змагання через участь у Чемпіонаті Світу 2024. Серед них Васін Віталій, Швед Олександр та Писарев Олексій.")
st.write("**** всі наведені рейтинги не є офіційними рейтингами федерації і розраховані автором цієї сторінки у мотиваційно-розважальних цілях.")
st.write("Контактна інформація: Telegram: @vitaliy_bashun")
