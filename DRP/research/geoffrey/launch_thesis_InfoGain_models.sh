python -u build_model.py -p @descs/InfoGain_nonzero_thesis.dsc -trs geoffrey_split_for_thesis_0 -tes geoffrey_split_for_thesis_1 -v -mt SVM_PUK_basic -d "geoffrey thesis SVM InfoGain_nonzero" &> SVM_basic_InfoGain_nonzero_thesis.out &
python -u build_model.py -p @descs/InfoGain_nonzero_thesis.dsc -trs geoffrey_split_for_thesis_0 -tes geoffrey_split_for_thesis_1 -v -mt SVM_PUK_BCR -d "geoffrey thesis BCR SVM InfoGain_nonzero" &> SVM_BCR_InfoGain_nonzero_thesis.out &
python -u build_model.py -p @descs/InfoGain_nonzero_thesis.dsc -trs geoffrey_split_for_thesis_0 -tes geoffrey_split_for_thesis_1 -v -mt KNN -d "geoffrey thesis BCR SVM InfoGain_nonzero" &> KNN_InfoGain_nonzero_thesis.out &
python -u build_model.py -p @descs/InfoGain_nonzero_thesis.dsc -trs geoffrey_split_for_thesis_0 -tes geoffrey_split_for_thesis_1 -v -mt J48 -d "geoffrey thesis BCR SVM InfoGain_nonzero" &> J48_InfoGain_nonzero_thesis.out &
python -u build_model.py -p @descs/InfoGain_nonzero_thesis.dsc -trs geoffrey_split_for_thesis_0 -tes geoffrey_split_for_thesis_1 -v -mt NaiveBayes -d "geoffrey thesis BCR SVM InfoGain_nonzero" &> NB_InfoGain_nonzero_thesis.out &
