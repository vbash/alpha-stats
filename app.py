import streamlit as st
import pandas as pd
import plotly.express as px
import pyarrow as pa

st.set_page_config(page_title="Alpha Stats Carbine", layout="wide")

df_schema = pa.schema([("rank_num", "int32"),
                       ("progress", "string"),
                       ("shooters_name", "string"),
                       ("rating", pa.float32()),
                       ("class", "string"),
                       ("class_avg", pa.decimal128(38, 9)),
                       ("matches", "int32"),
                       ("percents", pa.list_(pa.float32())),
                       ("places", pa.list_(pa.int32()))])


def print_rating_table(rating_file_path, category):
    rating_df = pd.read_parquet(rating_file_path, schema=df_schema)
    rating_df = rating_df.sort_values(by=['rank_num']).round(2).set_index(rating_df.columns[0]).rename(
        columns={'rank_num': 'Номер у рейтингу', 'rating': 'Рейтинг', 'class': 'Клас спортсмена',
                 'class_avg': 'Середній результат з 2х кращіх', 'matches': 'Кількість матчів'})

    rating_df['percents'] = rating_df['percents'].apply(lambda x: [round(i, 1) for i in x])

    rating_df_column_config = {
        "percents": st.column_config.BarChartColumn(
            "Останні 6 змаганнь",
            help="Відсотки від 1го місця",
            y_min=0,
            y_max=100,
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
        key=rating_file_path
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

    if len(event.selection.rows) > 0:
        df_shooters_history = pd.read_csv(file_path_shooter_rating_history, sep=",")
        filtered_df_shooters_history = df_shooters_history.loc[df_shooters_history['shooters_name'].isin(filtered_df['shooters_name'])]
        filtered_df_shooters_history_c = filtered_df_shooters_history.loc[
            filtered_df_shooters_history['rating_category'] == category]
        if len(event.selection.rows) == 1:
            # show shooters "analytical card"
            shooters_name = filtered_df.iloc[0]['shooters_name']
            column_config_rating_history = {
                "rating_date": "Дата",
                "rank_num": "Номер у рейтингу",
                "progress": "Прогрес",
                "rating": "Рейтинг",
                "class": "Клас"
            }
            st.title(shooters_name + " - історія рейтингу")
            st.dataframe(
                filtered_df_shooters_history_c,
                hide_index=True,
                column_config=column_config_rating_history,
                column_order=('rating_date', 'rank_num', 'progress', 'rating', 'class')
            )

        fig1 = px.line(
            filtered_df_shooters_history_c,
            x='rating_date',
            y=['rating'],
            color='shooters_name'
        )
        fig1.update_layout(yaxis_title="Рейтинг")  # Adjust the label
        fig1.update_layout(xaxis_title="Дата складання рейтингу")
        st.plotly_chart(fig1)

        fig2 = px.line(
            filtered_df_shooters_history_c,
            x='rating_date',
            y=['rank_num'],
            color='shooters_name'
        )
        fig2.update_yaxes(autorange="reversed")  # Invert the y-axis
        fig2.update_layout(yaxis_title="Місце у рейтингу")  # Adjust the label
        fig2.update_layout(xaxis_title="Дата складання рейтингу")
        st.plotly_chart(fig2)

        st.title("Останні 6 змаганнь")
        st.dataframe(filtered_df[['shooters_name', 'percents', 'places']], column_config=filtered_df_column_config)
        df_prc = pd.DataFrame(filtered_df['percents'].values.tolist(), index=filtered_df['shooters_name']).add_prefix(
            'percent')
        df_prc = df_prc.reset_index()
        df_prc = df_prc.reset_index()

        df_matches_prc = pd.read_csv(file_path_matches, sep=",")
        res_df0 = df_matches_prc.iloc[[0]].join(df_prc[['shooters_name', 'percent0']], how='cross')
        res_df1 = df_matches_prc.iloc[[1]].join(
            df_prc[['shooters_name', 'percent1']].rename(columns={'percent1': 'percent0'}), how='cross')
        res_df2 = df_matches_prc.iloc[[2]].join(
            df_prc[['shooters_name', 'percent2']].rename(columns={'percent2': 'percent0'}), how='cross')
        res_df3 = df_matches_prc.iloc[[3]].join(
            df_prc[['shooters_name', 'percent3']].rename(columns={'percent3': 'percent0'}), how='cross')
        res_df4 = df_matches_prc.iloc[[4]].join(
            df_prc[['shooters_name', 'percent4']].rename(columns={'percent4': 'percent0'}), how='cross')
        res_df5 = df_matches_prc.iloc[[5]].join(
            df_prc[['shooters_name', 'percent5']].rename(columns={'percent5': 'percent0'}), how='cross')
        res_df = pd.concat([res_df0, res_df1, res_df2, res_df3, res_df4, res_df5])

        fig3 = px.bar(
            res_df,
            x='match_date',
            y=['percent0'],
            color='shooters_name',
            barmode='group'
        )
        fig3.update_layout(yaxis_title="Відсотки від найкращого результату")  # Adjust the label
        fig3.update_layout(xaxis_title="Дата змаганнь")
        st.plotly_chart(fig3)


rating_release = 5
rating_bucket = "ipsc-rating"

extended_path = f"https://storage.googleapis.com/{rating_bucket}/{rating_release}/General.parquet"
extended_path_SAS = f"https://storage.googleapis.com/{rating_bucket}/{rating_release}/SAS.parquet"
extended_path_SAO = f"https://storage.googleapis.com/{rating_bucket}/{rating_release}/SAO.parquet"
extended_path_Lady = f"https://storage.googleapis.com/{rating_bucket}/{rating_release}/Lady.parquet"
extended_path_Senior = f"https://storage.googleapis.com/{rating_bucket}/{rating_release}/Senior.parquet"
extended_path_Junior = f"https://storage.googleapis.com/{rating_bucket}/{rating_release}/Junior.parquet"
file_path_matches = f"https://storage.googleapis.com/{rating_bucket}/{rating_release}/matches.csv"
file_path_club_rating = f"https://storage.googleapis.com/{rating_bucket}/{rating_release}/club_rating.csv"
file_path_club_rating_history = f"https://storage.googleapis.com/{rating_bucket}/{rating_release}/club_rating_history.csv"
file_path_club_lists = f"https://storage.googleapis.com/{rating_bucket}/{rating_release}/club_lists.csv"
file_path_shooter_rating_history = f"https://storage.googleapis.com/{rating_bucket}/{rating_release}/shooters_rating_history.csv"


st.title("Рейтинг спортсменів-стрільців. Практична стрільба. Карабін.")
st.write("Останне оновлення рейтингу 2024.08.04")
st.write("Таблиця рейтингів* та классів**")
print_rating_table(extended_path, 'General')

df = pd.read_parquet(extended_path, schema=df_schema).sort_values(by=['class_avg'])
fig_h1 = px.histogram(df, x="rating", nbins=10)
fig_h1.update_layout(xaxis_title="Рейтинг")
fig_h1.update_layout(yaxis_title="Кількість спортсменів")
fig_h2 = px.histogram(df, x="class")
fig_h2.update_layout(xaxis_title="Клас")
fig_h2.update_layout(yaxis_title="Кількість спортсменів")
st.write(fig_h1)
st.write(fig_h2)

st.write(
    "* для розрахунку рейтингу використовуються данні з останніх 6 матчів національного рівня (Чемпіонат України, "
    "Кубок України). Якщо спортсмен пропустив матч, то за такий матч спортсмен отримує свій середній результат "
    "помножений на 0.75. Далі результати за останні 6 матчів перемножуються на наступні коєфіцієнти: 1.0, 0.9, 0.8, "
    "0.7, 0.6, 0.5, тачим чином, що б матчі, які видбулись останніми, мали вищу вагу. Сума результатів і є рейтингом "
    "спортсмена. Максимальний теоретично можливий тейтинг складає 450 балів (потрібно виграти 6 останніх матчів).")
st.write(
    "** для розрахунку класса використовуються відсотки набрані спортсменом у останніх 6 матчах. З них беруться два "
    "найкращіх результата і обраховуєтся цередне значення цих двох найкращіх. Далі, відповідно до результатів "
    "вихначаються відповідні класи: Grand Master - 95-100%, Master - 85-94.9%, A - 75-84.9%, B - 60-74.9%, "
    "C - 40-59.9%, D - 2-39.9%")

st.title("SAO")
print_rating_table(extended_path_SAO, 'SAO')

st.title("SAS")
print_rating_table(extended_path_SAS, 'SAS')

st.title("Lady")
print_rating_table(extended_path_Lady, 'Lady')

st.title("Senior")
print_rating_table(extended_path_Senior, 'Senior')

st.title("Junior")
print_rating_table(extended_path_Junior, 'Junior')

st.title("Матчі враховані у рейтинг")
df_matches = pd.read_csv(file_path_matches, sep=",")
st.data_editor(
    df_matches,
    column_config={
        "num": "Номер",
        "name": "Назва",
        "match_date": "Дата",
        "results_link": st.column_config.LinkColumn(
            "Посилання на результати",
            help="Посилання на Practiscore результати",
            display_text="Перейти до результатів"
        )
    },
    hide_index=True,
    key="matches"
)

st.write(
    "*** підчас Кубку України 3 етап 2024, понижуючий коефіцієнт 0.75 не застосовувався для деяких спортсменів "
    "вимушено пропустивших змагання через участь у Чемпіонаті Світу 2024. Серед них Васін Віталій, Швед Олександр та "
    "Писарев Олексій.")

st.title("Рейтинг клубів")
df_club_rating = pd.read_csv(file_path_club_rating, sep=",")
df_club_rating = df_club_rating.sort_values(by=['rank']).reset_index()


clubs_column_config = {
    "rank": "Місце",
    "progress": "Прогрес",
    "club": "Клуб",
    "rating_sum": st.column_config.ProgressColumn(label="Рейтинг", format="%.2f", min_value=0, max_value=3000),
    "shooters_counted": "Кількість врахованих спортсменів",
}

club_selection_event = st.dataframe(
    df_club_rating,
    column_config=clubs_column_config,
    use_container_width=False,
    hide_index=True,
    on_select="rerun",
    selection_mode="multi-row",
    key="club",
    column_order=("rank", "progress", "club", "rating_sum", "shooters_counted")
)

df_club_lists = pd.read_csv(file_path_club_lists, sep=",")
df_club_rating_history = pd.read_csv(file_path_club_rating_history, sep=",")

if len(club_selection_event.selection.rows) == 1:
    club = df_club_rating.loc[club_selection_event.selection.rows[0], 'club']
    df_list = df_club_lists.loc[df_club_lists['club'] == club]

    list_column_config = {
        "club_rank": "Місце у клубі",
        "rank_num": "Місце у загальному рейтингу",
        "club": "Клуб",
        "shooters_name": "Спортсмен",
        "rating": "Рейтинг",
    }

    st.title(club)
    st.dataframe(
        df_list,
        column_config=list_column_config,
        hide_index=True,
    )

if len(club_selection_event.selection.rows) > 0:
    clubs = club_selection_event.selection.rows
    selected_clubs_df = df_club_rating.iloc[clubs]

    filtered_history_df = df_club_rating_history.loc[df_club_rating_history['club'].isin(selected_clubs_df['club'])]

    fig4 = px.line(
        filtered_history_df,
        x='rating_date',
        y=['rating_sum'],
        color='club'
    )
    fig4.update_layout(yaxis_title="Рейтинг")  # Adjust the label
    fig4.update_layout(xaxis_title="Дата")
    st.plotly_chart(fig4)

st.write("**** Рейтинг клубу розрахований як сумма райтингів 10 найсильніших спортсменів клубу")

st.write(
    "***** всі наведені рейтинги не є офіційними рейтингами федерації і розраховані автором цієї сторінки у "
    "мотиваційно-розважальних цілях.")
st.write("Контактна інформація: Telegram: @vitaliy_bashun")
