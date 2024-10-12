# SeamlessM4Tv2-API
Custom API endpoints for generating text-to-speech and speech-to-speech translation audio files, ready for deployment. 
<p> SeamlessM4T-v2 is a collection of models designed to provide high quality translation, allowing people from different linguistic communities to communicate effortlessly through speech and text. </p>

## Cloning and Installation
<p> Begin by cloning the repository onto your local machine using <code>git clone https://github.com/as9219/SeamlessM4Tv2-API.git</code>. Open your preffered IDE and make sure to have the latest version of Python installed.
<p> Next, install all the requirments using <code>pip install -r requirements.txt</code>

## Execution and Making Test Calls
Run the application in your IDE, a flask server should be running.

### Sample Curl Command
<code>curl -X POST -H "Content-Type: application/json" -d '{"text": "Hello World, I am making a text to speech curl command!", "src_lang": "eng", "tgt_lang": "fra"}' http://127.0.0.1:5000/t2s</code>

For deployment, download the latest version of <a href='https://www.docker.com/products/docker-desktop/'>Docker</a> and install it on your machine.
