import os
from pyexpat import model
import torch

import commons
import utils
from models import SynthesizerTrn

from scipy.io.wavfile import write

import text as text_utils


class vits_inference:
    def __init__(self, model_name):
        self.load_model(
            os.path.join("model", model_name, "config.json"),
            os.path.join("model", model_name, "model.pth"),
        )

    def get_text(self, text, hps):
        text_norm = text_utils.text_to_sequence(text, hps.data.text_cleaners)
        if hps.data.add_blank:
            text_norm = commons.intersperse(text_norm, 0)
        text_norm = torch.LongTensor(text_norm)
        return text_norm

    def load_model(self, config_file, model_file):
        self.hps = utils.get_hparams_from_file(config_file)
        self.net_g = SynthesizerTrn(
            len(text_utils.symbols),
            self.hps.data.filter_length // 2 + 1,
            self.hps.train.segment_size // self.hps.data.hop_length,
            **self.hps.model
        ).cuda()
        _ = self.net_g.eval()
        _ = utils.load_checkpoint(model_file, self.net_g, None)

    def synthesis(self, output_file, target_text, speaker_id=-1):
        stn_tst = self.get_text(target_text, self.hps)
        with torch.no_grad():
            x_tst = stn_tst.cuda().unsqueeze(0)
            x_tst_lengths = torch.LongTensor([stn_tst.size(0)]).cuda()
            if speaker_id != -1:
                sid = torch.LongTensor([int(speaker_id)]).cuda()
                audio = (
                    self.net_g.infer(
                        x_tst,
                        x_tst_lengths,
                        sid=sid,
                        noise_scale=0.667,
                        noise_scale_w=0.8,
                        length_scale=1,
                    )[0][0, 0]
                    .data.cpu()
                    .float()
                    .numpy()
                )
            else:
                audio = (
                    self.net_g.infer(
                        x_tst,
                        x_tst_lengths,
                        noise_scale=0.667,
                        noise_scale_w=0.8,
                        length_scale=1,
                    )[0][0, 0]
                    .data.cpu()
                    .float()
                    .numpy()
                )
            audio = audio * 32768.0
            audio = audio.squeeze()
            audio = audio.astype("int16")
            write(output_file, 22050, audio)


if __name__ == "__main__":
    model_name = input("模型名称：")
    output_dir = input("输出目录：")
    model = vits_inference(model_name)
    while True:
        target_text = input("生成文本：")
        output_file = os.path.join(
            output_dir, "{}_{}.wav".format(model_name, target_text.replace(" ", "_"))
        )
        model.synthesis(output_file, target_text)
        print("生成完成，输出文件：{}".format(output_file))
