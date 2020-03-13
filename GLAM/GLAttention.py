import torch
import torch.nn as nn
from cfg.config import cfg


def conv1x1(in_planes, out_planes):
    """1x1 convolution with padding"""
    return nn.Conv2d(in_planes, out_planes, kernel_size=1, stride=1,
                     padding=0, bias=False)


def func_attention(query, context, gamma1):
    """
    query: batch x ndf x queryL
    context: batch x ndf x ih x iw (sourceL=ihxiw)
    mask: batch_size x sourceL
    """
    batch_size, queryL = query.size(0), query.size(2)
    ih, iw = context.size(2), context.size(3)
    sourceL = ih * iw

    # --> batch x sourceL x ndf
    context = context.view(batch_size, -1, sourceL)
    contextT = torch.transpose(context, 1, 2).contiguous()

    # Get attention
    # (batch x sourceL x ndf)(batch x ndf x queryL)
    # -->batch x sourceL x queryL
    attn = torch.bmm(contextT, query)
    # --> batch*sourceL x queryL
    attn = attn.view(batch_size * sourceL, queryL)
    attn = nn.Softmax()(attn)  # Eq. (8)

    # --> batch x sourceL x queryL
    attn = attn.view(batch_size, sourceL, queryL)
    # --> batch*queryL x sourceL
    attn = torch.transpose(attn, 1, 2).contiguous()
    attn = attn.view(batch_size * queryL, sourceL)

    attn = attn * gamma1
    attn = nn.Softmax()(attn)
    attn = attn.view(batch_size, queryL, sourceL)
    # --> batch x sourceL x queryL
    attnT = torch.transpose(attn, 1, 2).contiguous()

    # (batch x ndf x sourceL)(batch x sourceL x queryL)
    # --> batch x ndf x queryL
    weightedContext = torch.bmm(context, attnT)

    return weightedContext, attn.view(batch_size, -1, ih, iw)


class GLAttentionGeneral(nn.Module):
    def __init__(self, idf, cdf):
        super(GLAttentionGeneral, self).__init__()
        self.conv_context = conv1x1(cdf, idf)  # idf <- ngf feature vector 32     cdf <- ef_dim  text embeding size
        # so conv1x1 takes in text_embedding   output  idf size
        self.conv_sentence_vis = conv1x1(idf, idf)
        self.linear = nn.Linear(100, idf)
        self.sm = nn.Softmax()
        self.mask = None

    def applyMask(self, mask):
        self.mask = mask  # batch x sourceL

    def forward(self, input, sentence, context):
        """
            input: batch x idf x ih x iw (queryL=ihxiw)

            context: batch x cdf x sourceL (this is the matrix of word vectors)

            sentence (c_code1): batch x idf x queryL (this is the vectors of the sentence)
            queryL=ih x iw
        """
        # input 16, 32, 64, 64
        # sentence 16, 100 (not 16 256 because of CA net)
        # context 16, 256, 18
        idf, ih, iw = input.size(1), input.size(2), input.size(
            3)  # input batch x ngf feature size x image height x image width
        queryL = ih * iw  # query length = height x width = 64 x 64 =  4096
        batch_size, sourceL = context.size(0), context.size(2)  # batch_size = 16, source length = 18

        # generated image feature:--> batch x queryL x idf
        target = input.view(batch_size, -1, queryL)  # batch x idf x queryL    (16, 32, 4096)
        targetT = torch.transpose(target, 1, 2).contiguous()  # batch x queryL x idf    (16, 4096, 32)

        # Eq(4) in MirrorGAN : local-level attention
        # words feature:  batch x cdf x sourceL --> batch x cdf x sourceL x 1     16, 256, 18
        sourceT = context.unsqueeze(3)  # (16, 256, 18, 1)
        # --> batch x idf x sourceL
        sourceT = self.conv_context(sourceT).squeeze(
            3)  # (16, 256, 18, 1) -> (16, 32, 18) this make the contiguous for the tensor https://stackoverflow.com/questions/48915810/pytorch-contiguous

        attn = torch.bmm(targetT, sourceT)  # (16, 4096, 32) bmm (16, 32, 18)  =  (16, 4096, 18)
        # --> batch*queryL x sourceL
        attn = attn.view(batch_size * queryL, sourceL)  # (16 * 4096, 18)
        if self.mask is not None:
            # batch_size x sourceL --> batch_size*queryL x sourceL
            mask = self.mask.repeat(queryL, 1)
            attn.data.masked_fill_(mask.data, -float('inf'))
        attn = self.sm(attn)  # Eq. (2)
        # --> batch x queryL x sourceL
        attn = attn.view(batch_size, queryL, sourceL)
        # --> batch x sourceL x queryL
        attn = torch.transpose(attn, 1, 2).contiguous()

        # (batch x idf x sourceL)(batch x sourceL x queryL)
        # --> batch x idf x queryL
        weightedContext = torch.bmm(sourceT, attn)  # (16, 32, 18) bmm (16, 18, 4096) = (16, 32, 4096)
        weightedContext = weightedContext.view(batch_size, -1, ih, iw)  # batch x idf x ih x iw -> (16, 32, 64, 64)
        word_attn = attn.view(batch_size, -1, ih, iw)  # (batch x sourceL x ih x iw) -> (16, 18, 64, 64)

        # Eq(5) in MirrorGAN : global-level attention
        sentence = self.linear(sentence)
        sentence = sentence.view(batch_size, idf, 1, 1)
        sentence = sentence.repeat(1, 1, ih, iw)  # for each pixel we gave all the feature in the sent_embedding
        sentence_vs = torch.mul(input, sentence)  # batch x idf x ih x iw   apply the attention
        sentence_vs = self.conv_sentence_vis(sentence_vs)  # batch x idf x ih x iw
        # sent_att = nn.Softmax()(sentence_vs)  # batch x idf x ih x iw    softmax along batch
        # different to the original code
        sent_att = sentence_vs.view(batch_size * ih * iw, idf)
        sent_att = nn.Softmax()(sent_att)
        sent_att = sent_att.view(batch_size, idf, ih, iw)

        # weightedSentence = torch.mul(sentence, sent_att)  # batch x idf x ih x iw
        if cfg.GAN.GLOBAL_ATTEN_ON:
            weightedSentence = torch.mul(sentence, sent_att)
        else:
            weightedSentence = sentence
        return weightedContext, weightedSentence, word_attn, sent_att

        # weightedContext: batch x idf x ih x iw
        # weightedSentence: batch x idf x ih x iw
        # word_attn: batch x sourceL x ih x iw
        # sent_vs_att: batch x idf x ih x iw
