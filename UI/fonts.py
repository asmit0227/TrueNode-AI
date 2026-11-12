import streamlit as st

def Fonts_styling():
   
      st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Alfa+Slab+One&family=Archivo+Black&family=Black+Ops+One&family=Jockey+One&family=Lato:ital,wght@0,100;0,300;0,400;0,700;0,900;1,100;1,300;1,400;1,700;1,900&family=Open+Sans:ital,wght@0,300..800;1,300..800&family=Outfit:wght@100..900&display=swap');
         h1{
             font-family : "Black Ops One" , sans-serif !important;
             font-size : 3.5rem !important;
             line-height : 2.4rem important;
             margin-bottom : 0rem !important
        } 

         h2{
                 font-family : "Alfa Slab One" , sans-serif !important;
                             font-size : 3rem !important;
                             font-weight : 700!important
                             line-height : 0.8 !important;
                             margin-bottom : 0rem !important;
                             margin-top: 6rem !important;
                             display: flex !important;
                             justify-content: center !important;
                             align-items: center !important;     
             
                              } 
              h3,h4{
                          font-family : "Outfit" , sans-serif !important;
                          
                          font-weight : 700!important;
                          font-size : 2rem !important;
                         line-height : 0.8 !important;
                        margin-bottom : 0rem !important;
                          display: flex !important;
                        justify-content: center !important; 
                        align-items: center !important;     
                        }  
                    p{
                          font-family : "Outfit" , sans-serif !important;
                          
                          font-weight : 700!important;
                          font-size : 1.2rem !important;
                         line-height : 0.8 !important;
                        margin-bottom : 0rem !important;
                          display: flex !important;
                        justify-content: center !important; 
                        align-items: center !important;     
                          
                       }   
                button{
                     border-radius :1.5rem !important;
                     background : #5865F2 !important;
                     color : white !important;
                     padding : 10px 20px !important;
                     border : none !important;
                     transition : transform 0.25s ease-in-out !important;
                     }       
               button[kind="secondary"]{
                     border-radius :1.5rem !important;
                     background : #000000 !important;
                     color : white !important;
                     padding : 10px 20px !important;
                     border : none !important;
                     transition : transform 0.25s ease-in-out !important;
           }  
         button[kind="tertiary"]{
                      border-radius :1.5rem !important;
                      background : black !important;
                      color : white !important;
                      padding : 10px 20px !important;
                      border : none !important;
                      transition : transform 0.25s ease-in-out !important;
                      }  
         button:hover{
            transform : scale(1.05)
         }               

             

        
        
        
        </style>
                      """, 
                      unsafe_allow_html=True)
             