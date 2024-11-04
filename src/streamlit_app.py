import streamlit as st

from dataclasses import asdict
from streamlit_keycloak import login

from delta import get_cpr_search, get_dq_number_search, search  # , get_general_search
from utils import set_logging_configuration, verify_cpr, get_cpr_list
from config import KEYCLOAK_URL, KEYCLOAK_REALM, KEYCLOAK_CLIENT

set_logging_configuration()

st.set_page_config(page_title="Telefonbog", page_icon="📞")
st.markdown('<style>table {width:100%;}</style>', unsafe_allow_html=True)

keycloak = login(
    url=KEYCLOAK_URL,
    realm=KEYCLOAK_REALM,
    client_id=KEYCLOAK_CLIENT
)

if keycloak.authenticated:
    st.write(f"Du er logget ind som {keycloak.user_info['preferred_username']}")

    st.session_state.USER = {'username': keycloak.user_info['preferred_username'], 'email': keycloak.user_info['email']}
    roles = asdict(keycloak).get('user_info', {}).get('resource_access', {}).get(KEYCLOAK_CLIENT, {}).get('roles', [])

    if 'cpr' in roles:
        st.session_state.CPR = True

    if "USER" not in st.session_state:
        st.session_state.USER = None

    if "CPR" not in st.session_state:
        st.session_state.CPR = False

    if "search" not in st.session_state:
        st.session_state.search = None

    if "error" not in st.session_state:
        st.session_state.error = None

    def cpr_change():
        if st.session_state.CPR:
            st.session_state.free = ""
            st.session_state.dq = ""
            if st.session_state.cpr:
                if verify_cpr(st.session_state.cpr):
                    st.session_state.search = get_cpr_search(st.session_state.cpr, st.session_state.USER, st.session_state.CPR)
                    st.session_state.error = None
                else:
                    st.session_state.error = "Ugyldigt CPR-nummer"
                    st.session_state.search = None
        else:
            st.session_state.error = "Du har ikke de rigtgige rettigheder til at søge på CPR-numre"

    # Removed - not working as intended
    # def free_change():
    #     st.session_state.cpr = ""
    #     st.session_state.dq = ""
    #     st.session_state.error = None
    #     if st.session_state.free:
    #         st.session_state.search = get_general_search(st.session_state.free, st.session_state.USER)

    def dq_change():
        st.session_state.cpr = ""
        st.session_state.free = ""
        st.session_state.error = None
        if st.session_state.dq:
            st.session_state.search = get_dq_number_search(st.session_state.dq, st.session_state.USER)

    st.title('Telefonbog')

    seacrh, lookup = st.tabs(["Find medarbejder", "Slå e-mails op med cpr-numre"])

    with seacrh:
        left_column, right_column = st.columns(2)

        with left_column:
            st.text_input("CPR-nummer", placeholder="CPR-nummer", key="cpr", on_change=cpr_change, disabled=not st.session_state.CPR)

            # st.text_input("Søg (max 100 resultater)", placeholder="Navn, email eller telefonnummer", key="free", on_change=free_change) # Removed - not working as intended

        with right_column:
            st.text_input("DQ-nummer", placeholder="Brugernavn", key="dq", on_change=dq_change)

        if st.session_state.error:
            st.error(st.session_state.error)
        if st.session_state.search:
            with st.spinner('Søger...'):
                try:
                    if st.session_state.search:
                        result = search(st.session_state.search, st.session_state.USER)
                        if result:
                            if len(result) == 1:
                                r = result[0]
                                with st.expander(r['Navn'], expanded=True):
                                    top_line = '| ' + ' | '.join(['Navn', 'DQ-nummer', 'Afdeling']) + ' |' + '\n| ' + ' | '.join(['---']*3) + ' |' + '\n| ' + ' | '.join([r['Navn'], r['DQ-nummer'], r['Afdeling']]) + ' |'
                                    buttom_line = '| ' + ' | '.join(['E-mail', 'Telefon', 'Mobil']) + ' |' + '\n| ' + ' | '.join(['---']*3) + ' |' + '\n| ' + ' | '.join([r['E-mail'], r['Telefon'], r['Mobil']]) + ' |'
                                    st.markdown(top_line)
                                    st.markdown(buttom_line)
                            elif len(result) > 1:
                                for r in result:
                                    with st.expander(r['Navn'], expanded=False):
                                        top_line = '| ' + ' | '.join(['Navn', 'DQ-nummer', 'Afdeling']) + ' |' + '\n| ' + ' | '.join(['---']*3) + ' |' + '\n| ' + ' | '.join([r['Navn'], r['DQ-nummer'], r['Afdeling']]) + ' |'
                                        buttom_line = '| ' + ' | '.join(['E-mail', 'Telefon', 'Mobil']) + ' |' + '\n| ' + ' | '.join(['---']*3) + ' |' + '\n| ' + ' | '.join([r['E-mail'], r['Telefon'], r['Mobil']]) + ' |'
                                        st.markdown(top_line)
                                        st.markdown(buttom_line)
                            else:
                                st.write("Ingen resultater")
                        else:
                            st.write("Ingen resultater")
                except Exception as e:
                    st.error(f'Fejl: {e}')
    with lookup:
        txt = st.text_area(label="CPR-numre", placeholder="Indsæt CPR-numre her - adskildt med ' , ' (komma)", disabled=not st.session_state.CPR)

        disable_button = True

        if txt:
            if get_cpr_list(txt) and st.session_state.CPR:
                disable_button = False
                st.write("Tryk på knappen 'Slå e-mails op' for at få e-mails for indtastede CPR-numre")
            else:
                st.error('Ugyldigt CPR-nummer')

        if st.button("Slå e-mails op", disabled=disable_button):
            with st.spinner('Søger...'):
                try:
                    cpr_list = get_cpr_list(txt)
                    if cpr_list:
                        cpr_dict_list = [get_cpr_search(cpr, st.session_state.USER, st.session_state.CPR) for cpr in cpr_list]
                        search_result = [search(cpr_dict, st.session_state.USER) for cpr_dict in cpr_dict_list]
                        email_list = [r[0]['E-mail'] if r[0]['DQ-nummer'] != '-' else 'IKKE_FUNDET' for r in search_result]
                        emails = f'''{','.join(email_list)}'''
                        st.code(emails)
                    else:
                        st.error('Ugyldigt CPR-nummer')
                except Exception as e:
                    st.error(f'Fejl: {e}')

else:
    st.write("Du er ikke logget ind")
