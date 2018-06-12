import json
import numpy as np
import pandas as pd
from keras.models import model_from_json
from typeAD import RLenv
import matplotlib.pyplot as plt
from typeAD import huber_loss


if __name__ == "__main__":
    formated_test_path = "../../datasets/formated/formated_test_type.data"


    with open("models/type_model.json", "r") as jfile:
        model = model_from_json(json.load(jfile))
    model.load_weights("models/type_model.h5")
#    with open("models/defender_agent_model.json", "r") as jfile:
#        model = model_from_json(json.load(jfile))
#    model.load_weights("models/defender_agent_model.h5")
    
    model.compile(loss=huber_loss,optimizer="sgd")

    # Define environment, game, make sure the batch_size is the same in train
    env = RLenv('test',formated_test_path = formated_test_path)
    
    total_reward = 0
    
    true_labels = np.zeros(len(env.attack_types),dtype=int)
    estimated_labels = np.zeros(len(env.attack_types),dtype=int)
    estimated_correct_labels = np.zeros(len(env.attack_types),dtype=int)
    
    states , labels = env.get_full()
    q = model.predict(states)
    actions = np.argmax(q,axis=1)        
    
    true_labels += np.sum(labels).values

    for indx,a in enumerate(actions):
        estimated_labels[a] +=1              
        if a == np.argmax(labels.iloc[indx].values):
            total_reward += 1
            estimated_correct_labels[a] += 1
    
    
        
    Accuracy = estimated_correct_labels / true_labels
    Mismatch = abs(estimated_correct_labels - true_labels)+abs(estimated_labels-estimated_correct_labels)

    print('\r\nTotal reward: {} | Number of samples: {} | Accuracy = {}%'.format(total_reward,
          len(states),float(100*total_reward/len(states))))
    outputs_df = pd.DataFrame(index = env.attack_types,columns = ["Estimated","Correct","Total","Acuracy","Mismatch"])
    for indx,att in enumerate(env.attack_types):
       outputs_df.iloc[indx].Estimated = estimated_labels[indx]
       outputs_df.iloc[indx].Correct = estimated_correct_labels[indx]
       outputs_df.iloc[indx].Total = true_labels[indx]
       outputs_df.iloc[indx].Acuracy = Accuracy[indx]*100
       outputs_df.iloc[indx].Mismatch = abs(Mismatch[indx])


        
    print(outputs_df)
    
    #%%
    
    ind = np.arange(1,len(env.attack_types)+1)
    fig, ax = plt.subplots()
    width = 0.35
    p1 = plt.bar(ind, estimated_correct_labels,width,color='g')
    p2 = plt.bar(ind, 
                 (np.abs(estimated_correct_labels-true_labels)\
                  +np.abs(estimated_labels-estimated_correct_labels)),width,
                 bottom=estimated_correct_labels,color='r')

    
    ax.set_xticks(ind)
    ax.set_xticklabels(env.attack_types,rotation='vertical')
    #ax.set_yscale('log')

    #ax.set_ylim([0, 100])
    ax.set_title('Test set scores')
    plt.legend((p1[0], p2[0]), ('Correct estimated', 'Incorrect estimated'))
    plt.tight_layout()
    #plt.show()
    plt.savefig('results/test_type_improved.eps', format='eps', dpi=1000)
