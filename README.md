**this repo is under construction**

<hr>

*This repo is unofficial reproduction of paper [MirrorGAN: Learning Text-to-image Generation by Redescription](https://arxiv.org/abs/1903.05854)*

#### Dataset

- Preprocess

```bash
python2 preprocess.py
```

#### Pretrain

- STEM

```bash
cd STEM
python2 pretrain_DAMSM.py
```

- STREAM

```bash
cd STREAM
python2 train.py
```

- Pertained Model

  Coming...

#### Train

```bash
cd GLAM
python2 mian.py
```

#### Test

```bash
cd GLAM
python2 mian.py --cfg cfg/eval_bird.yml
```

#### Contact

[ZHAO WANG](mailto:kyfafyd@zju.edu.cn)

#### License

- MIT





