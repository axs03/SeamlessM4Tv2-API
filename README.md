# SeamlessM4Tv2-API
Custom API endpoints for generating text-to-speech and speech-to-speech translation audio files, ready for deployment. 
<p> SeamlessM4T-v2 is a collection of models designed to provide high quality translation, allowing people from different linguistic communities to communicate effortlessly through speech and text. </p>

## Cloning and Installation
<p> Begin by cloning the repository onto your local machine using <code>git clone https://github.com/as9219/SeamlessM4Tv2-API.git</code>. Open your preferred IDE and make sure to have the latest version of Python installed.
<p> Next, install all the requirments using <code>pip install -r requirements.txt</code>

## Execution and Making Test Calls
Run the application in your IDE, a flask server should be running.

### Sample Curl Command
<code>curl -X POST -H "Content-Type: application/json" -d '{"text": "Hello World, I am making a text to speech curl command!", "src_lang": "eng", "tgt_lang": "fra"}' {flask_localhost_url}/t2s</code>
<br>
<br>
<code>curl -X POST -H "Content-Type: multipart/form-data" -F "file=path/to/audio_file.wav" -F "tgt_lang=eng" {flask_localhost_url}/s2s</code>


## Containerizing Using Docker
For containerizing, download the latest version of <a href='https://www.docker.com/products/docker-desktop/'>Docker</a> and install it on your machine. <br>
Make sure Docker is running. You can check by using <code>docker --version</code>.<br>
Navigate to <code>your/project/path</code> for this project. Type <code>docker build -t SeamlessM4Tv2-API</code> in your terminal. Docker will now build the container. Run the container by using 
