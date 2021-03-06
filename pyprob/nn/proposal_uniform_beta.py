import torch
import torch.nn as nn

from .. import util
from . import EmbeddingFeedForward
from ..distributions import Beta


class ProposalUniformBeta(nn.Module):
    def __init__(self, input_shape, output_shape, num_layers=3):
        super().__init__()
        self._output_dim = util.prod(output_shape)
        self._output_shape = torch.Size([-1]) + output_shape
        self._ff = EmbeddingFeedForward(input_shape=input_shape, output_shape=torch.Size([self._output_dim * 2]), num_layers=num_layers, activation=torch.relu, activation_last=torch.relu)

    def forward(self, x, prior_variables):
        x = self._ff(x)
        concentration1s = 1. + x[:, :self._output_dim].view(self._output_shape)
        concentration0s = 1. + x[:, self._output_dim:].view(self._output_shape)
        prior_lows = torch.stack([v.distribution.low for v in prior_variables]).view(concentration1s.size())
        prior_highs = torch.stack([v.distribution.high for v in prior_variables]).view(concentration1s.size())
        return Beta(concentration1s, concentration0s, low=prior_lows, high=prior_highs)
