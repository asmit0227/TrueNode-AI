import streamlit as st

def header_homes():
   
    logo ="https://i.ibb.co/Zzkcb47T/truenode-AI-logo.png"

    st.markdown(
        f"""
        <div style="display : flex; flex-direction : column; align-items:center; justify-content:center; margin-bottom:0px; margin-top:0px;">
               <img src='{logo}' style= 'height:200px;border-radius:10px;'>
               <h1 style =" text-align:center;
                color:#000000;
                margin:10px 0 0 0;
                padding:0;
                line-height:1;
                letter-spacing:2px;">
                  <div style="letter-spacing:8px;">
                    TrueNode-AI
                  </div>
               <h1>  

                
                 
        </div>
        """,
         unsafe_allow_html=True
    )