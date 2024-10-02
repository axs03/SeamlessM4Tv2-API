# init.py

# note install with:
# pip install git+SeamlessM4Tv2Model, AutoProcessorM4Tv2Model, AutoProcessorgithub.com/huggingface/transformers.git sentencepiece

from transformers import SeamlessM4Tv2Model, AutoProcessor
import torch
import scipy
import torchaudio 

def initialize_model():
    if torch.backends.mps.is_available():
        device = torch.device("mps")
        print("running on mps")
    elif torch.cuda.is_available():
        device = torch.device("cuda")
        print("running on cuda")
    else:
        device = torch.device("cpu")
        print("running on cpu")
    device = "cpu" #temp fix for cuda issue
    processor = AutoProcessor.from_pretrained("facebook/seamless-m4t-v2-large")
    model = SeamlessM4Tv2Model.from_pretrained("facebook/seamless-m4t-v2-large")
    model = model.to(torch.device(device))
    return model, processor, device

model, processor, device = initialize_model()

# t2s translation
def text_to_speech(text: str, src_lang: str, tgt_lang: str, output_path: str):
    text_inputs = processor(text = text, src_lang=src_lang, return_tensors="pt").to(device)
    audio_array_from_text = model.generate(**text_inputs, tgt_lang=tgt_lang)[0].cpu().numpy().squeeze()
    scipy.io.wavfile.write(output_path, rate=16000, data=audio_array_from_text)

# s2s translation
def speech_to_speech(file_path: str, tgt_lang: str, output_path: str):
    ### note audio is a tensor of the .wav, and also returns the inital sample rate

    audio, orig_freq = torchaudio.load(uri=file_path, format='wav', backend="soundfile") # pip install soundfile
    if orig_freq!= 16000:
        audio =  torchaudio.functional.resample(audio, orig_freq, new_freq=16000) # must be a 16 kHz waveform array
    audio_inputs = processor(audios=audio , sampling_rate=16000,return_tensors="pt").to(device)
    audio_array_from_audio = model.generate(**audio_inputs, tgt_lang=tgt_lang)[0].cpu().numpy().squeeze()
    scipy.io.wavfile.write(output_path, rate=16000, data=audio_array_from_audio)

