import numpy as np
from MineSweeper import MineSweeper
import time
import os
import pdb
import matplotlib.pyplot as plt

class MineSweeperLearner:
    def __init__(self, name, model):
        self.name = name
        self.model = model
        self.dim1 = 16
        self.dim2 = 30
        self.totalCells = self.dim1*self.dim2

    # ultimately want to put this in the model so each can extract its own shit
    def getPredictorsFromGameState(self, state):
        out = np.zeros((11, self.dim1, self.dim2))
        # channel 0: cell number "holds contains information", i.e. has been revealed
        out[0] = np.where(np.isnan(state), 0, 1)
        # channel 1: cell is on game board (useful for detecting edges when conv does 0 padding)
        out[1] = np.ones((self.dim1, self.dim2))
        # the numeric channels: one layer each for 0 to 8 neighbors; one-hot encoding
        for i in range(0, 9):
            out[i + 2] = np.where(state == i, 1, 0)
        return out

    def learnMineSweeper(self, nSamples, nBatches, nEpochsPerBatch, verbose=True, nhwcFormat=True):
        X = np.zeros((nSamples, 11, self.dim1, self.dim2))  # 11 channels: 1 for if has been revealed, 1 for is-on-board, 1 for each number
        X2 = np.zeros((nSamples, 1, self.dim1, self.dim2))
        y = np.zeros((nSamples, 1, self.dim1, self.dim2))

        cellsRevealedTimeSeries = open("log/%s-%d" % (self.name, time.time()), "w")
        cellsRevealedTimeSeriesAvg = open("log/%s-batch-mean-%d" % (self.name, time.time()), "w")


        for i in range(nBatches):
            # pdb.set_trace()
            totalCellsRevealed = 0
            gamesPlayed = 0
            gamesWon = 0
            samplesTaken = 0
            while samplesTaken < nSamples:
                # initiate game
                game = MineSweeper()
                #print("Starting new game")
                # pdb.set_trace()
                #pick middle on first selection. better than corner.
                game.selectCell((int(self.dim1 / 2), int(self.dim2 / 2)))
                while not (game.gameOver or samplesTaken == nSamples):
                    # get data input from game state
                    Xnow = self.getPredictorsFromGameState(game.state)
                    # pdb.set_trace()
                    X[samplesTaken] = Xnow
                    X2now = np.array([np.where(Xnow[0] == 0, 1, 0)])
                    X2[samplesTaken] = X2now

                    # make probability predictions
                    if nhwcFormat:
                        out = self.model.predict([np.array([Xnow.transpose((1, 2, 0))]), np.array([X2now.transpose((1, 2, 0))])])
                    else:
                        out = self.model.predict([np.array([Xnow]), np.array([X2now])])

                    # choose best remaining cell
                    # pdb.set_trace()
                    orderedProbs = np.argsort((out[0, :, :, 0] if nhwcFormat else out[0][0]) + Xnow[0], axis=None) #add Xnow0 so that already selected cells aren't chosen
                    selected = orderedProbs[0]
                    selected1 = int(selected / self.dim2)
                    selected2 = selected % self.dim2
                    # pdb.set_trace()
                    game.selectCell((selected1, selected2))
                    # find truth
                    truth = out
                    if nhwcFormat:
                        truth[0, selected1, selected2, 0] = game.mines[selected1, selected2]
                    else:
                        truth[0, 0, selected1, selected2] = game.mines[selected1, selected2]
                    y[samplesTaken] = truth[0].transpose([2, 0, 1]) if nhwcFormat else truth[0]
                    samplesTaken += 1

                    #print("At sample %d of %d" % (samplesTaken, nSamples))
                    #print("Cells revealed in current game: %d" % (self.totalCells - np.sum(np.isnan(game.state))))

                if game.gameOver:
                    gamesPlayed += 1
                    cellsRevealed = self.totalCells - np.sum(np.isnan(game.state))
                    #cellsRevealedTimeSeries.write(str(cellsRevealed))
                    #cellsRevealedTimeSeries.write('\n')
                    totalCellsRevealed += cellsRevealed
                    if game.victory:
                        gamesWon += 1
                    #print("Cells revealed in current game: %d" % cellsRevealed)
                    #print("Total cells trained on (revealed): %d" % totalCellsRevealed)
                    #print("Samples taken: %d" % samplesTaken)
                    #print("Games won: %d" % gamesWon)
                    #pdb.set_trace()

            #cellsRevealedTimeSeries.flush()
            meanCellsRevealed = -1
            propGamesWon = -1
            if gamesPlayed > 0:
                meanCellsRevealed = float(totalCellsRevealed) / gamesPlayed
                propGamesWon = float(gamesWon) / gamesPlayed
                cellsRevealedTimeSeriesAvg.write(str(meanCellsRevealed))
                cellsRevealedTimeSeriesAvg.write("\n")
                cellsRevealedTimeSeriesAvg.flush()
            if verbose:
                print("Games played, batch " + str(i) + ": " + str(gamesPlayed))
                print("Mean cells revealed, batch " + str(i) + ": " + str(meanCellsRevealed))
                print("Proportion of games won, batch " + str(i) + ": " + str(propGamesWon))
            #train
            self.model.fit([X.transpose((0, 2, 3, 1)), X2.transpose((0, 2, 3, 1))], y.transpose((0, 2, 3, 1)), batch_size=nSamples, epochs=nEpochsPerBatch)
            #save it every 2
            if (i+1) % 2 == 0:
                self.model.save("trainedModels/" + self.name + ".h5")
                #pdb.set_trace()
                print("Saved to %s" % (self.name + ".h5"))

    def testMe(self, nGames):
        cellsRevealed = 0
        gamesWon = 0
        for i in range(nGames):
            if (i % 10) == 0:
                print("Playing game " + str(i+1) + "...")
            # initiate game
            game = MineSweeper()
            # pick middle on first selection. better than corner.
            game.selectCell((int(self.dim1 / 2), int(self.dim2 / 2)))
            while not game.gameOver:
                # get data input from game state
                Xnow = self.getPredictorsFromGameState(game.state)
                X2now = np.array([np.where(Xnow[0] == 0, 1, 0)])
                # make probability predictions
                out = self.model.predict([np.array([Xnow]), np.array([X2now])])
                # choose best remaining cell
                orderedProbs = np.argsort(out[0][0] + Xnow[0], axis=None)  # add Xnow[0] so that already selected cells aren't chosen
                selected = orderedProbs[0]
                selected1 = int(selected / self.dim2)
                selected2 = selected % self.dim2
                game.selectCell((selected1, selected2))
            cellsRevealed += self.totalCells - np.sum(np.isnan(game.state))
            if game.victory:
                gamesWon += 1
        meanCellsRevealed = float(cellsRevealed) / nGames
        propGamesWon = float(gamesWon) / nGames
        print("Proportion of games won, batch " + str(i) + ": " + str(propGamesWon))
        print("Mean cells revealed, batch " + str(i) + ": " + str(meanCellsRevealed))


    def watchMePlay(self):
        play = True
        while play:
            game = MineSweeper()
            os.system("clear")
            print("Beginning play")
            print("Game board:")
            print(game.state)
            #make first selection in the middle. better than corner.
            selected1 = int(self.dim1/2)
            selected2 = int(self.dim2/2)
            game.selectCell((selected1, selected2))
            time.sleep(0.05)
            os.system("clear")
            #now the rest
            while not game.gameOver:
                print("Last selection: (" + str(selected1+1) + "," + str(selected2+1) + ")")
                if 'out' in locals():
                    print("Confidence: " + str(np.round(100*(1-np.amin(out[0][0] + Xnow[0])),2)) + "%")
                print("Game board:")
                print(game.state)
                Xnow = self.getPredictorsFromGameState(game.state)
                X2now = np.array([np.where(Xnow[0] == 0, 1, 0)])
                # make probability predictions
                out = self.model.predict([np.array([Xnow]), np.array([X2now])])
                # choose best remaining cell
                orderedProbs = np.argsort(out[0][0] + Xnow[0], axis=None)  # add Xnow[0] so that already selected cells aren't chosen
                selected = orderedProbs[0]
                selected1 = int(selected / self.dim2)
                selected2 = selected % self.dim2
                game.selectCell((selected1, selected2))
                time.sleep(0.05)
                os.system("clear")
            print("Last selection: (" + str(selected1+1) + "," + str(selected2+1) + ")")
            print("Confidence: " + str(np.round(100 * (1 - np.amin(out[0][0] + Xnow[0])), 2)) + "%")
            print("Game board:")
            print(game.state)
            if game.victory:
                print("Victory!")
            else:
                print("Game Over")
            get = input("Watch me play again? (y/n): ")
            if get != "y":
                play = False
