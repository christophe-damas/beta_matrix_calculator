import streamlit as st
import pandas as pd

from beta_matrix_calc import return_beta_values, ticker_list

ranked_beta_df = pd.DataFrame()
btc_beta_df = pd.DataFrame()
eth_beta_df = pd.DataFrame()
ranked_zscore = pd.DataFrame()
btc_zscore = pd.DataFrame()
eth_zscore = pd.DataFrame()

about = open("about.txt", "r")

st.set_page_config(
    page_title="Beta Matrix Calculator",
    page_icon="📊",
    layout="wide"
)

st.title("***:green[Beta] Matrix Calculator App***")

with st.expander("Description:"):
    st.markdown(about.read())

# Function to execute beta calculation
def execute_calculation():
    global btc_beta_df, eth_beta_df, ranked_beta_df, btc_zscore, eth_zscore, ranked_zscore
    btc_beta_df, eth_beta_df, ranked_beta_df, btc_zscore, eth_zscore, ranked_zscore = return_beta_values(
        [b_c_1, b_c_2, b_c_3, b_c_4],
        market_tickers
    )


# Beta Calculation Inputs Form
with st.form("calc_inputs"):
    st.write("Calculation Inputs")
    row1 = st.columns([1, 1, 1, 1])
    b_c_1 = row1[0].number_input('Beta Calculation Length 1', min_value=1, step=1, value=30)
    b_c_2 = row1[1].number_input('Beta Calculation Length 2', min_value=1, step=1, value=90)
    b_c_3 = row1[2].number_input('Beta Calculation Length 3', min_value=1, step=1, value=120)
    b_c_4 = row1[3].number_input('Beta Calculation Length 4', min_value=1, step=1, value=200)
    market_tickers = st.multiselect('Select Beta Assets', ticker_list())
    st.form_submit_button('Calculate Beta Matrix', on_click=execute_calculation())

if ranked_beta_df.empty:
    st.write("Calculated Matrix Tables will appear her as soon as your selection is submitted.")

# Display Ranked Beta Values if available
if not ranked_beta_df.empty:
    row_ranked = st.columns([1, 1])
    row_ranked[0].write("Ranked Beta Values")
    row_ranked[0].dataframe(ranked_beta_df, hide_index=1)
    row_ranked[1].write("Ranked Z-Scored Beta Values")
    row_ranked[1].dataframe(ranked_zscore, hide_index=1)


# Display BTC Beta Values if available
if not btc_beta_df.empty:
    row_btc = st.columns([1, 1])
    row_btc[0].write("BTC Beta Values")
    row_btc[0].dataframe(btc_beta_df, hide_index=1)
    row_btc[1].write("Z-Scored BTC Beta Values")
    row_btc[1].dataframe(btc_zscore, hide_index=1)


# Display ETH Beta Values if available
if not eth_beta_df.empty:
    row_eth = st.columns([1, 1])
    row_eth[0].write("ETH Beta Values")
    row_eth[0].dataframe(eth_beta_df, hide_index=1)
    row_eth[1].write("Z-Scored ETH Beta Values")
    row_eth[1].dataframe(eth_zscore, hide_index=1)

st.divider()
st.write('''Beta Matrix Calculator App 2024\n
         This site is for informational purposes only. The information on our website is not financial advice, and you should not consider it to be financial advice.''')
