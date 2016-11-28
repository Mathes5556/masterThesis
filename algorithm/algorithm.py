import pandas as pd
import numpy as np


def fSelection(data):
    columns = ["uuid", "action", "pot", "levelOfBetting", "roundCount", "isOnSmallblind", "isOnBigBlind"
        , "smallBlindAmount", "bigBlindAmount", "stackOfPlayer", "stackOfOpponent", "sklanskyClass",
               "EHS", "HS", "PPOT", "NPOT", "handStrengthFromLibrary", "opponentAgressivnessScore",
               "opponentAgressivnessScoreLast7Round",
               "winnerOfRound", "finalPotInGame"]

    df = pd.DataFrame()
    for column in columns:
        if column == "action":
            values = []
            for v in data[column]:
                if v == "call":
                    values.append(1)
                elif v == "fold":
                    values.append(0)
                else:
                    values.append(2)
        else:
            values = [val for val in data[column]]
        df[column] = values

    isWinnerColumn = []

    for index, row in df.iterrows():
        uuid, uuidOfWinner = row["uuid"], row["winnerOfRound"]
        if uuid == uuidOfWinner:
            isWinnerColumn.append(1)
        # rewards.append(1)
        else:
            isWinnerColumn.append(-1)
            # rewards.append(-1)

    df['isWinnerColumn'] = isWinnerColumn
    # df['rewards'] = rewards


    del df['winnerOfRound']
    del df['uuid']
    return df


data = pd.read_csv("historyC.csv")
print(len(data))
data = data[data.levelOfBetting == 1]
print(len(data))

data = fSelection(data)
print(data)

####### reinforcment learning #########

import tensorflow as tf
import numpy as np


class contextual_bandit():
    def __init__(self):
        self.state = 0
        # List out our bandits. Currently arms 4, 2, and 1 (respectively) are the most optimal.
        self.bandits = np.array([[0.2, 0, -0.0, -5], [0.1, -5, 1, 0.25], [-5, 5, 5, 5]])
        self.num_bandits = self.bandits.shape[0]
        self.num_actions = self.bandits.shape[1]

    def getBandit(self):
        self.state = np.random.randint(0, len(self.bandits))  # Returns a random state for each episode.
        return self.state

    def pullArm(self, action):
        # Get a random number.
        bandit = self.bandits[self.state, action]
        result = np.random.randn(1)
        if result > bandit:
            # return a positive reward.
            return 1
        else:
            # return a negative reward.
            return -1


def forwardprop(X, w_1, w_2):
    """
    Forward-propagation.
    IMPORTANT: yhat is not softmax since TensorFlow's softmax_cross_entropy_with_logits() does that internally.
    """
    h = tf.nn.sigmoid(tf.matmul(X, w_1))  # The \sigma function
    yhat = tf.matmul(h, w_2)  # The \varphi function
    return yhat


def init_weights(shape):
    """ Weight initialization """
    weights = tf.random_normal(shape, stddev=0.1)
    return tf.Variable(weights)


class agent():
    def __init__(self, lr, input_size, outputSize):

        # These lines established the feed-forward part of the network. The agent takes a state and produces an action.
        self.state_in = tf.placeholder(shape=[1, input_size], dtype=tf.float32)
        print("self.state_in ", self.state_in )
        #         print(state_in_OH)
        # Layer's sizes
        x_size = input_size  # Number of input nodes: 4 features and 1 bias
        h_size = input_size * 2  # Number of hidden nodes
        y_size = outputSize  # Number of outcomes (3 iris flowers)


        # Weight initializations
        w_1 = init_weights((x_size, h_size))
        w_2 = init_weights((h_size, y_size))

        # Forward propagation
        output = forwardprop(self.state_in, w_1, w_2)
        #         print("yhat_self.output", output)
        self.output = tf.reshape(output, [-1])
        print("output", output)
        print("self.output", self.output)

        #         print("yhatReshape", yhatReshape)

        #         print("state_in_OH", state_in_OH)
        #         output = slim.fully_connected(state_in_OH,a_size,\
        #             biases_initializer=None,activation_fn=tf.nn.sigmoid,weights_initializer=tf.ones_initializer)
        #         print(output)
        #         self.output = tf.reshape(output,[-1])
        #         print("self.output", self.output)
        self.chosen_action = tf.argmax(self.output, 0)

        # The next six lines establish the training proceedure. We feed the reward and chosen action into the network
        # to compute the loss, and use it to update the network.
        self.reward_holder = tf.placeholder(shape=[1], dtype=tf.float32)
        print("self.reward_holder", self.reward_holder)
        self.action_holder = tf.placeholder(shape=[1], dtype=tf.int32)
        print("self.action_holder", self.action_holder)
        self.responsible_weight = tf.slice(self.output, self.action_holder, [1])

        print("responsible_weight", self.responsible_weight)
        self.loss = -(tf.log(self.responsible_weight) * self.reward_holder)
        optimizer = tf.train.GradientDescentOptimizer(learning_rate=lr)
        self.update = optimizer.minimize(self.loss)


inputs, actions, rewards = [], [], []
for index, row in data.iterrows():
    inputToAlgorithm = list(row)  # delete action and isWinnerColumn values
    inputToAlgorithm = inputToAlgorithm[:-2]
    inputs.append(inputToAlgorithm)
    action = [int(row["action"] == 0), int(row["action"] == 1), int(row["action"] == 2)]
    action = int(row["action"])
    actions.append(action)
    reward = row["isWinnerColumn"]
    rewards.append(reward)

INPUT_SIZE = len(inputs[0])
OUTPUT_SIZE = 3
print INPUT_SIZE, OUTPUT_SIZE

tf.reset_default_graph()  # Clear the Tensorflow graph.

# cBandit = contextual_bandit()  # Load the bandits.
# reward = cBandit.pullArm(1)  # Get our reward for taking an action given a bandit.
# action = np.random.randint(cBandit.num_actions)
# print(reward)
# print action
# exit()
myAgent = agent(lr=0.001, input_size=INPUT_SIZE, outputSize=OUTPUT_SIZE)  # Load the agent.
weights = tf.trainable_variables()[0]  # The weights we will evaluate to look into the network.

total_episodes = 10000  # Set total number of episodes to train agent on.
total_reward = np.zeros([INPUT_SIZE, OUTPUT_SIZE])  # Set scoreboard for bandits to 0.
e = 0.1  # Set the chance of taking a random action.

init = tf.initialize_all_variables()

# Launch the tensorflow graph



with tf.Session() as sess:
    sess.run(init)
    i = 0


    while i < total_episodes:

        for input, action, reward in zip(inputs, actions, rewards):
            #print input
            # s = [0.0, 0.0, 1.0]  # cBandit.getBandit() #Get a state from the environment.
            # Choose either a random action or one from our network.
            # if np.random.rand(1) < e:
            #     action = np.random.randint(cBandit.num_actions)
            # else:
            #     action = sess.run(myAgent.chosen_action, feed_dict={myAgent.state_in: [s]})

            # reward = cBandit.pullArm(action)  # Get our reward for taking an action given a bandit.
            # prit(reward)
            # exit()
            #action = 1
            #         print("reward", reward)
            # Update the network.
            feed_dict = {myAgent.reward_holder: [reward], myAgent.action_holder: [action], myAgent.state_in: [input]}
            _, ww = sess.run([myAgent.update, weights], feed_dict=feed_dict)

            # Update our running tally of scores.
            # total_reward[input, action] += reward
            # if i % 500 == 0:
            #     print "Mean reward for each of the " + str(cBandit.num_bandits) + " bandits: " + str(
            #         np.mean(total_reward, axis=1))
            i += 1
            #
    print(ww)
    print "predict"
    right, bad = 0,0
    for input, action, reward in zip(inputs, actions, rewards):
        predictAction = sess.run(myAgent.chosen_action, feed_dict={myAgent.state_in: [input]})
        if predictAction == action:
            right += 1
        else:
            bad += 1
    print(right, bad)
    # feed_dict = {myAgent.reward_holder: [reward], myAgent.action_holder: [action], myAgent.state_in: [input]}
    # _, ww = sess.run([myAgent.update, weights], feed_dict=feed_dict)

# for a in range(cBandit.num_bandits):
#     print "The agent thinks action " + str(np.argmax(ww[a]) + 1) + " for bandit " + str(
#         a + 1) + " is the most promising...."
#     if np.argmax(ww[a]) == np.argmin(cBandit.bandits[a]):
#         print "...and it was right!"
#     else:
#         print "...and it was wrong!"