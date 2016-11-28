import pandas as pd
import numpy as np

def fSelection(data):
    columns = [ "uuid", "action", "pot", "levelOfBetting", "roundCount", "isOnSmallblind", "isOnBigBlind"
    ,"smallBlindAmount", "bigBlindAmount", "stackOfPlayer", "stackOfOpponent", "sklanskyClass",
    "EHS", "HS", "PPOT", "NPOT",  "handStrengthFromLibrary", "opponentAgressivnessScore", "opponentAgressivnessScoreLast7Round",
    "winnerOfRound"]

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
        uuid, uuidOfWinner =  row["uuid"], row["winnerOfRound"]
        if uuid == uuidOfWinner:
            isWinnerColumn.append(1)
        else:
            isWinnerColumn.append(0)
    df['isWinnerColumn'] = isWinnerColumn
    del df['winnerOfRound']
    del df['uuid']
    return df

data = pd.read_csv("historyC.csv")
print(len(data))

data = fSelection(data)
print(data)


msk = np.random.rand(len(data)) < 0.6
train = data[msk]
test = data[~msk]

####### reinforcment learning #########

import tensorflow as tf
import tensorflow.contrib.slim as slim
import numpy as np

class agent():
    def __init__(self, lr, s_size,a_size):
        #These lines established the feed-forward part of the network. The agent takes a state and produces an action.
        self.state_in= tf.placeholder(shape=[1, 3],dtype=tf.int32)
#         state_in_OH = slim.one_hot_encoding(self.state_in,s_size)
#         print(state_in_OH)
        output = slim.fully_connected(self.state_in,a_size,\
            biases_initializer=None,activation_fn=tf.nn.sigmoid,weights_initializer=tf.ones_initializer)
        self.output = tf.reshape(output,[-1])
        self.chosen_action = tf.argmax(self.output,0)
        #The next six lines establish the training proceedure. We feed the reward and chosen action into the network
        #to compute the loss, and use it to update the network.
        self.reward_holder = tf.placeholder(shape=[1],dtype=tf.float32)
        self.action_holder = tf.placeholder(shape=[1],dtype=tf.int32)
        self.responsible_weight = tf.slice(self.output,self.action_holder,[1])
        self.loss = -(tf.log(self.responsible_weight)*self.reward_holder)
        optimizer = tf.train.GradientDescentOptimizer(learning_rate=lr)
        self.update = optimizer.minimize(self.loss)


tf.reset_default_graph()  # Clear the Tensorflow graph.

myAgent = agent(lr=0.001, s_size=4, a_size=4)  # Load the agent.
weights = tf.trainable_variables()[0]  # The weights we will evaluate to look into the network.

total_episodes = 10000  # Set total number of episodes to train agent on.
total_reward = np.zeros([4, 3])  # Set scoreboard for bandits to 0.
e = 0.1  # Set the chance of taking a random action.

init = tf.initialize_all_variables()

# Launch the tensorflow graph
with tf.Session() as sess:
    sess.run(init)
    i = 0
    while i < total_episodes:
        s = [1, 2, 3]  # Get a state from the environment.
        # Choose either a random action or one from our network.
        #         if np.random.rand(1) < e:
        #             action = np.random.randint(cBandit.num_actions)
        #         else:
        #             action = sess.run(myAgent.chosen_action,feed_dict={myAgent.state_in:[s]})
        action = 1
        #         reward = cBandit.pullArm(action) #Get our reward for taking an action given a bandit.
        reward = 10
        # Update the network.
        feed_dict = {myAgent.reward_holder: [reward], myAgent.action_holder: [action], myAgent.state_in: [s]}
        _, ww = sess.run([myAgent.update, weights], feed_dict=feed_dict)

        # Update our running tally of scores.
        total_reward[s, action] += reward