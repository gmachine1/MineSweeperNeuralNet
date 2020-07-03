**该仓库被转移到中国版 github 码云 gitee 了。最新的版本在 https://gitee.com/gmachine1729/MineSweeperNeuralNet 。**

# MineSweeperNeuralNet
Teaching a neural network to play mine sweeper.

Watch the MinesweeperAIVideo file to see it in action. Or run watchMePlay.py and choose model7 to run it locally. Victory rate is currently around 42% on "Expert": a 16x30 board with 99 mines. See the requirements.txt file if you're having trouble.

See the powerpoint presentation for an explanation of the model structure.

To train a new model or continue training a saved one, run trainModel.py.

The goal of this project is to experiment with reinforcement learning, whereby general-purpose neural networks learn to do a task simply by doing it many times and getting some performance feedback. The model doesn’t know the rules of minesweeper, but it figures out how to play anyway. The model here is a convolutional neural network.

How good is ~42%? As a benchmark, another AI with hard-coded Minesweeper logic (including specific end-game strategies) achieved about 50% success on expert (https://luckytoilet.wordpress.com/2012/12/23/2125/). Hopefully the neural net gets there.

## 安装

以下被操作在**优麒麟 (Ubuntu Kylin) 19.10**上，PyCharm，及 Python 3.7 虚拟环境。

中国不翻墙把镜像改成清华的
```buildoutcfg
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```
然后安装
```buildoutcfg
pip install -r requirements.txt --timeout 100000
```

运行训练为
```buildoutcfg
python trainModel.py
```

直接训练可运行
```buildoutcfg
python trainModelBackground.py -o trainNew -m model7Mom -b 1000 -s 1000 -e 1 >log/model7Mom.out 
```
