
###################################
#!/usr/local/bin/python3
# CS B551 Fall 2019, Assignment #3
#
# Your names and user ids:
#   Nikita Bafna nibafna
#   Neha Pai nrpai
#   Shivali Jejurkar sjejurka
#
#


import sys
import os
import re
import math


#Global variables
bag_of_word = {}
bag_of_word['sp']={}
bag_of_word['nsp']={}
uniqueWord=[]

def generateBagOfWords(msg,sp):

    stop_word=('the','From:','To:', 'a','an','From','To',':',',','and')
    i=0
    for w in msg:
        if w.isalpha():                 # Only when the word is an alphabet add it to the bag
            if w not in uniqueWord:
                uniqueWord.append(w)
            if  w not in bag_of_word[sp]:
                bag_of_word[sp][w] = 1
            else:
                bag_of_word[sp][w] = bag_of_word[sp][w]+1



def cleanData(msg):
    print("Inside clean data")
    stop_words=('the','From:','To:', 'a','an','From','To',':',',','and')
    clean_data=[]

    for line in msg:
        # Remove escape
        line = re.sub('[!@#$.=<>/:&%^*,]', '', line)
        line = re.sub('[0-9]', '', line)
        line=line.replace("\\","")

        words = line.strip().split(" ")
        for word in words:
            word.lower()
            if (1<len(word)<20) and word not in stop_words and word.isalpha():
                clean_data.append(word)
    return clean_data


# For each file - read the content ,clean data and add to bag of words
def readMails(spam_dir,notspam_dir):
    print("Inside readmails")
    noOfSpam=0
    noOfNotSpam = 0

    for filename in os.listdir(spam_dir):
        with open(spam_dir + '/' + filename, encoding="Latin-1") as f:
            msg = f.readlines()
            cleanedData= cleanData(msg)
            generateBagOfWords(cleanedData,'sp')
            f.close()
        noOfSpam+=1

    for filename in os.listdir(notspam_dir):
        with open(notspam_dir + '/' + filename, encoding="Latin-1") as f:
            msg = f.readlines()
            cleanedData = cleanData(msg)
            generateBagOfWords(cleanedData,'nsp')
            f.close()
        noOfNotSpam += 1

    return bag_of_word,noOfSpam,noOfNotSpam


def calcLikelihood(sp, nsp):
    vocab = len(bag_of_word)

    l=['sp','nsp']
    likelihood = {}
    likelihood['sp'] = {}
    likelihood['nsp'] = {}
    for e in l:
        for w in uniqueWord:
            if w in bag_of_word[e]:
                num=bag_of_word[e][w]+1
            else:
                num=1
            deno = len(bag_of_word[e]) + len(uniqueWord)
            if e == 'sp':
                likelihood[e][w + '| S'] = -math.log(float(num / deno))
            elif e == 'nsp':
                likelihood[e][w + '| not S'] = -math.log(float(num / deno))
    return likelihood




def classify(likelihood,postProb,testDir,outputFile):
    print("Inside Classify")
    output_file = open(outputFile+".txt", 'w')

    ans={}
    for filename in os.listdir(testDir):
        with open(testDir + '/' + filename, encoding="Latin-1") as f:
            msg = f.readlines()
            cleanTestData = cleanData(msg)
            f.close()
            sprob= postProb['spam']
            for e in cleanTestData:
                if e not in bag_of_word['sp']:
                    sprob+=0.01
                else:
                    sprob+= likelihood['sp'][e+'| S']

            nsprob =postProb['not spam']
            for e in cleanTestData:
                if e not in bag_of_word['nsp']:
                    nsprob+=0.01
                else:
                    nsprob+=likelihood['nsp'][e+'| not S']

        print(sprob,nsprob)
        if sprob > nsprob:
            output_file.write(filename + " " + "spam"+"\n")
        elif sprob < nsprob:
            output_file.write(filename+ " "+"notspam"+"\n")

########### MAIN METHOD ###################

if __name__=="__main__":
    if len(sys.argv) < 4:
        print("Usage: \n../spam.py training-directory testing-directory output-file")
        sys.exit()

(train_dir, test_dir) = sys.argv[1:3]
dir_path = os.path.dirname(os.path.abspath(__file__))

spam_dir = os.path.join(dir_path,train_dir,"spam")
notspam_dir = os.path.join(dir_path,train_dir,"notspam")

output_file=sys.argv[3]



#Read mails to generate bag of words model
bag_of_word,spam,notSpam = readMails(spam_dir,notspam_dir)


#Calculate posterior probabilities:
postProb = {}
postProb['spam'] = float(spam/(spam+notSpam))
postProb['not spam'] = float(notSpam/(spam+notSpam))

#print("No of spam and not spam mails",spam,notSpam)
#print("Posterior probabilities",postProb)
#print(bag_of_word)

# Calculate likehood values for spam and non spam
likelihood= calcLikelihood('sp','nsp')


#saveData={'like':like,'postProb':postProb}
testDir=os.path.join(dir_path,test_dir)

# Classify the test data
classify(likelihood,postProb,testDir,output_file)
