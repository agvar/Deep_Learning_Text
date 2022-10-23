Install Streamlit on Windows- link :https://docs.streamlit.io/library/get-started/installation#install-streamlit-on-windows

Streamlit's officially-supported environment manager on Windows is Anaconda Navigator.

Install Anaconda
If you don't have Anaconda install yet, follow the steps provided on the Anaconda installation page.

Create a new environment with Streamlit
Next you'll need to set up your environment.

Follow the steps provided by Anaconda to set up and manage your environment using the Anaconda Navigator.

Select the "▶" icon next to your new environment. Then select "Open terminal":

In the terminal that appears, type:

`pip install streamlit`

Test that the installation worked:

`streamlit hello`

Streamlit's Hello app should appear in a new tab in your web browser!
[streamlit_screen]()

Use your new environment
In Anaconda Navigator, open a terminal in your environment (see step 2 above).

In the terminal that appears, use Streamlit as usual:

`streamlit run myfile.py`