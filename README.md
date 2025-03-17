# SeamlessM4Tv2-API
Custom API endpoints for generating text-to-speech and speech-to-speech translation audio files, ready for deployment. 
<p> SeamlessM4T-v2 is a collection of models designed to provide high quality translation, allowing people from different linguistic communities to communicate effortlessly through speech and text. </p>

## Cloning and Installation
Begin by cloning the repository onto your host machine using 
``` gitignore
git clone https://github.com/as9219/SeamlessM4Tv2-API.git
```
Open your preferred IDE and make sure to have the latest version of Python installed.
Next, install all the requirments and run locally using 
``` bat
pip install -r requirements.txt
```
<br>
<br>

## Containerizing Using Docker
For containerization, download the latest version of <a href='https://www.docker.com/products/docker-desktop/'>Docker</a> and install it on your machine. <br>
Make sure Docker is running. You can Docker is running by using:
#### MacOS
``` bash
ps -ef | grep docker
```
#### Windows
``` bash
docker info
```

<br>Now, we are ready to build our first image version! Open a terminal window in the project directory and use the following command:
``` bash
docker build -t SeamlessAPI:v1.0 .
```
Docker will now build the source code into an <i>image</i>. This process will take <code>~12 minutes</code> depending on your machine. <br>
Once this image is built, we can now peoceed to building the <i>container</i> using:
``` bash
docker run [OPTIONS] -p 8080:8080 --name seamlessapi_container SeamlessAPI:v1.0
```

You can have the following options for building the container:
| **[OPTIONS]** | **About** |
| -------- | ------------ |
| <code>-d</code> | Runs in detached mode, will not display any logs in terminal |
| <code>--privileged</code> | Runs container with heightened privileges |
| <code>--gpus all</code> | Use if you have GPUs available in your host machine for the container to use |

Docker builds the container and now our endpoints are ready for querying!
<br>
<br>

## Querying the Endpoints
There are the following endpoints
<ul>
  <li> T2S </li>
  <li> S2S </li>
</ul>

### Query Commands - macOS / Linux
#### T2S
``` bash
curl -X POST -H "Content-Type: application/json" -d '{"text": "Hello World, I am making a text to speech curl command!", "src_lang": "eng", "tgt_lang": "fra"}' http://localhost:8080/t2s --output path/to/outputdir/output.wav
```

#### S2S
``` bash
curl -X POST -H "Content-Type: multipart/form-data" -F "file=path/to/audio_file.wav" -F "tgt_lang=eng" http://localhost:8080/s2s --output path/to/outputdir/output.wav
```

### Query Commands - Windows
#### T2S (PowerShell)
``` powershell
Invoke-WebRequest -Uri "http://localhost:8080/t2s" -Method Post `
  -ContentType "application/json" `
  -Body '{"text": "Hello World, I am making a text to speech cli command!", "src_lang": "eng", "tgt_lang": "fra"}' `
  -OutFile "path\to\outputdir\output.wav"
```

#### S2S (PowerShell)
``` powershell
Invoke-WebRequest -Uri "http://localhost:8080/s2s" -Method Post `
  -Form @{ 
    file = Get-Item 'path\to\audio_file.wav'
    tgt_lang = 'eng'
  } `
  -OutFile "path\to\outputdir\output.wav"
```

### cURL command paramaters
| **Name**        | **Importance**     | **Description**                    |
|---------------------|----------|------------------------------------|
| text                | <code>required</code> | Any text you would like to convert |
| src_lang            | <code>optional</code> | default: eng                       |
| tgt_lang            | <code>optional</code> | default: fra                       |


<br>
