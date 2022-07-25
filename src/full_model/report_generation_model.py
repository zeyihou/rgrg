from typing import Optional, Tuple

import torch
import torch.nn as nn

from src.encoder.classification_model import ClassificationModel
from src.decoder.gpt2 import DecoderModel


class ReportGenerationModel(nn.Module):
    """
    Full model consisting of classifier encoder and decoder.
    """
    def __init__(self):
        super().__init__()
        self.encoder = ClassificationModel(return_feature_vectors=True)
        path_to_best_weights = "/u/home/tanida/weights/classification_model/weight_runs_2/val_loss_53.536_epoch_11.pth"
        self.encoder.load_state_dict(torch.load(path_to_best_weights))
        self.decoder = DecoderModel()

    def forward(self,
                images: torch.FloatTensor,  # images is of shape [batch_size, 1, 224, 224] (gray-scale images of size 224 x 224)
                input_ids: torch.LongTensor,  # shape (batch_size x seq_len)
                attention_mask: torch.FloatTensor,  # shape (batch_size x seq_len)
                return_loss: bool = False,
                past_key_values: Optional[Tuple[Tuple[torch.Tensor]]] = None,
                position_ids: Optional[torch.LongTensor] = None,
                use_cache: Optional[bool] = False
                ):
        image_features = self.encoder(images)  # image features of shape [batch_size, 1024]

        decoder_output = self.decoder(
            input_ids,
            attention_mask,
            image_features,
            return_loss,
            past_key_values,
            position_ids,
            use_cache
        )

        return decoder_output

    @torch.no_grad()
    def generate(self,
                 images: torch.FloatTensor,  # images is of shape [batch_size, 1, 224, 224] (gray-scale images of size 224 x 224)
                 max_length: int = None,
                 num_beams: int = 1,
                 num_beam_groups: int = 1,
                 do_sample: bool = False,
                 num_return_sequences: int = 1,
                 early_stopping: bool = False
                 ) -> torch.LongTensor:  # shape (batch_size x longest_generated_sequence_length)
        """
        Generates output ids for a batch of images.
        These output ids can then be decoded by the tokenizer to get the generated sentences.
        """
        image_features = self.encoder(images)  # image features of shape [batch_size, 1024]
        output_ids = self.decoder.generate(
            image_features,
            max_length,
            num_beams,
            num_beam_groups,
            do_sample,
            num_return_sequences,
            early_stopping)

        return output_ids  # shape (batch_size x longest_generated_sequence_length)