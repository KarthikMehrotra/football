import streamlit as st
import altair as alt
import pandas as pd

url='https://drive.google.com/file/d/1fgh0gCpHYSHLwtzei9GLtwOoCm-YKiKc/view?usp=sharing'
url='https://drive.google.com/uc?id=' + url.split('/')[-2]
df = pd.read_csv(url)



# app

# sidebar



# filters

seasons = list(df['SEASON'].drop_duplicates())
seasons_choice = st.sidebar.slider(
    'Season Range:', min_value=2014, max_value=2020, step=1, value=2020)
df = df[df['SEASON'] <= seasons_choice]

leagues = list(df['LEAGUE'].drop_duplicates())
leagues_choice = st.sidebar.multiselect(
    'Choose Leagues:', leagues, default=leagues)
df = df[df['LEAGUE'].isin(leagues_choice)]

home_teams = list(df['HOME'].drop_duplicates())
away_teams = list(df['AWAY'].drop_duplicates())
teams = list(set().union(home_teams, away_teams))
teams.sort()
teams_choice = teams
if st.sidebar.checkbox('Choose Teams:'):
    teams_choice = st.sidebar.multiselect(
        '', teams, default=teams)
df = df[df['HOME'].isin(teams_choice)]
df = df[df['AWAY'].isin(teams_choice)]

positions = ['GK', 'DC', 'DL', 'DR', 'DMC', 'DML', 'DMR', 'MC',
             'ML', 'MR', 'AMC', 'AML', 'AMR', 'FW', 'FWL', 'FWR', 'Sub']
positions_choice = positions
if st.sidebar.checkbox('Choose Positions:'):
    positions_choice = st.sidebar.multiselect(
        '', positions, default=positions)
df = df[df['POSITION'].isin(positions_choice)]

# main

st.title(f"Footverse")
st.markdown("""---""")

# stats dashboard

# cache!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# st.table make it static and not interactive!!!!!!!!!!!!!!!!!!!!!!!!

total_df = df.groupby(['PLAYER_NAME']).sum().drop(
    ['GAMEID', 'SUBSTITUTEIN', 'SEASON', 'HOMEGOALS', 'AWAYGOALS'], axis=1)
total_df['GOALS+ASSISTS'] = total_df['GOALS']+total_df['ASSISTS']
total_df['90s'] = total_df['TIME']/90
calc_elements = ['GOALS', 'SHOTS', 'ASSISTS', 'KEYPASSES']
for each in calc_elements:
    total_df[f'{each}_p90'] = total_df[each] / total_df['90s']
index_col = total_df.index
total_df['PLAYER_NAME'] = index_col
players = df['PLAYER_NAME'].drop_duplicates().sort_values(ascending=True)
players_index = players.index
player_leagues = df.loc[players_index, 'LEAGUE']
total_df['LEAGUE'] = player_leagues.tolist()
appearances = df['PLAYER_NAME'].value_counts().to_frame().rename(
    columns={'PLAYER_NAME': 'APPEARANCES'})
total_df = total_df.join(appearances)

# select box for selecting various stats
selectbox_option = st.selectbox('Choose the Stat:',
                                ('Top Goalscorers', 'Top Assist Providers', 'Most Goal Involvements (G+A)', 'Goals vs Shots', 'Assists vs Keypasses', 'p90 Key Metrics', 'Most Booked Players', 'Most Goals Scored in a Single Game', 'Most Assists Provided in a Single Game', 'Most Entertaining Games'))
if (selectbox_option == 'Top Goalscorers'):
    left_column, right_column = st.columns(2)
    most_goals = total_df[['GOALS', 'APPEARANCES']].sort_values([
        'GOALS'], ascending=False)
    left_column.dataframe(most_goals)
    right_column.bar_chart(most_goals.drop(['APPEARANCES'], axis=1).head(10))

if (selectbox_option == 'Top Assist Providers'):
    left_column, right_column = st.columns(2)
    most_assists = total_df[['ASSISTS', 'APPEARANCES']].sort_values([
        'ASSISTS'], ascending=False)
    left_column.dataframe(most_assists)
    right_column.bar_chart(most_assists.drop(['APPEARANCES'], axis=1).head(10))

if (selectbox_option == 'Most Goal Involvements (G+A)'):
    left_column, right_column = st.columns(2)
    most_goals_assists = total_df[['GOALS+ASSISTS', 'GOALS', 'ASSISTS',
                                   'APPEARANCES']].sort_values(['GOALS+ASSISTS'], ascending=False)
    left_column.dataframe(most_goals_assists)
    right_column.bar_chart(most_goals_assists.drop(
        ['GOALS+ASSISTS', 'APPEARANCES'], axis=1).head(10))
if (selectbox_option == 'Goals vs Shots'):
    goals_vs_shots = total_df[['GOALS', 'SHOTS', 'PLAYER_NAME', 'LEAGUE']]
    goals_vs_shots["EFFECTIVENESS"] = goals_vs_shots['GOALS'] / \
        goals_vs_shots['SHOTS']
    st.dataframe(goals_vs_shots.sort_values(
        ['GOALS'], ascending=False).drop(['PLAYER_NAME', 'LEAGUE'], axis=1))
    # align to right!!!!!!!!!!!!!!!!!
    st.write('Top 50 Goalscorers only*')
    # try matplot (pyplot) charts!!!!!!!!!!!!!!!!!
    goals_vs_shots_chart = alt.Chart(goals_vs_shots.sort_values(['GOALS'], ascending=False).head(50)).mark_circle().encode(
        x='GOALS', y='SHOTS', size='EFFECTIVENESS', color='LEAGUE', tooltip=['PLAYER_NAME', 'GOALS', 'SHOTS', 'EFFECTIVENESS'])
    st.altair_chart(goals_vs_shots_chart, use_container_width=True)

if (selectbox_option == 'Assists vs Keypasses'):
    assists_vs_keypasses = total_df[[
        'ASSISTS', 'KEYPASSES', 'PLAYER_NAME', 'LEAGUE']]
    assists_vs_keypasses["EFFECTIVENESS"] = assists_vs_keypasses['ASSISTS'] / \
        assists_vs_keypasses['KEYPASSES']
    st.dataframe(assists_vs_keypasses.sort_values(
        ['ASSISTS'], ascending=False).drop(['PLAYER_NAME', 'LEAGUE'], axis=1))
    # align to right!!!!!!!!!!!!!!!!!
    st.write('Top 50 Assist Providers only*')
    # try matplot (pyplot) charts!!!!!!!!!!!!!!!!!
    assists_vs_keypasses_chart = alt.Chart(assists_vs_keypasses.sort_values(['ASSISTS'], ascending=False).head(50)).mark_circle().encode(
        x='ASSISTS', y='KEYPASSES', size='EFFECTIVENESS', color='LEAGUE', tooltip=['PLAYER_NAME', 'ASSISTS', 'KEYPASSES', 'EFFECTIVENESS'])
    st.altair_chart(assists_vs_keypasses_chart, use_container_width=True)
if (selectbox_option == 'p90 Key Metrics'):
    p90_table = total_df[['GOALS_p90',
                          'ASSISTS_p90', 'SHOTS_p90', 'KEYPASSES_p90', '90s']]
    mean_90s = p90_table['90s'].mean()
    p90_table = p90_table[p90_table['90s'] >= mean_90s]
    left_column, right_column = st.columns(2)
    left_column.bar_chart(p90_table[['GOALS_p90']].sort_values(
        ['GOALS_p90'], ascending=False).head(10))
    right_column.bar_chart(p90_table[['ASSISTS_p90']].sort_values(
        ['ASSISTS_p90'], ascending=False).head(10))
    left_column.bar_chart(p90_table[['SHOTS_p90']].sort_values(
        ['SHOTS_p90'], ascending=False).head(10))
    right_column.bar_chart(p90_table[['KEYPASSES_p90']].sort_values(
        ['KEYPASSES_p90'], ascending=False).head(10))
    st.dataframe(p90_table.drop(['90s'], axis=1))
    st.write('**Data displayed for players with ',
              '* minutes played at the least*')

if (selectbox_option == 'Most Booked Players'):
    left_column, right_column = st.columns(2)
    most_booked_players = df[['PLAYER_NAME', 'YELLOWCARD', 'REDCARD']]
    total_bookings = df['YELLOWCARD']+df['REDCARD']
    most_booked_players['TOTAL_BOOKINGS'] = total_bookings
    most_booked_players = most_booked_players.groupby(
        ['PLAYER_NAME']).sum().sort_values(['TOTAL_BOOKINGS'], ascending=False)
    most_booked_players = most_booked_players[[
        'TOTAL_BOOKINGS', 'YELLOWCARD', 'REDCARD']]
    left_column.dataframe(most_booked_players)
    right_column.bar_chart(most_booked_players.drop(
        ['TOTAL_BOOKINGS'], axis=1).head(10))

if (selectbox_option == 'Most Goals Scored in a Single Game'):
    max_goals = df[df['GOALS'] == df['GOALS'].max()]
    st.dataframe(max_goals[['GOALS', 'PLAYER_NAME', 'HOME',
                            'AWAY', 'HOMEGOALS', 'AWAYGOALS', 'DATE']])
if (selectbox_option == 'Most Assists Provided in a Single Game'):
    max_assists = df[df['ASSISTS'] == df['ASSISTS'].max()]
    st.dataframe(max_assists[['ASSISTS', 'PLAYER_NAME', 'HOME',
                              'AWAY', 'HOMEGOALS', 'AWAYGOALS', 'DATE']])

if (selectbox_option == 'Most Entertaining Games'):
    most_entertaining_games = df.drop_duplicates(['GAMEID']).drop(
        ['PLAYER_NAME', 'GOALS', 'OWNGOALS', 'ASSISTS', 'SHOTS', 'KEYPASSES', 'POSITION', 'YELLOWCARD', 'REDCARD', 'TIME', 'SUBSTITUTEIN'], axis=1)
    most_entertaining_games['HOMEGOALS+AWAYGOALS'] = most_entertaining_games['HOMEGOALS'] + \
        most_entertaining_games['AWAYGOALS']
    most_entertaining_games = most_entertaining_games[[
        'HOME', 'AWAY', 'HOMEGOALS', 'AWAYGOALS', 'HOMEGOALS+AWAYGOALS', 'LEAGUE', 'SEASON', 'DATE']]
    st.dataframe(most_entertaining_games.sort_values(
        ['HOMEGOALS+AWAYGOALS'], ascending=False))
