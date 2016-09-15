#!/usr/bin/python3

#====================================================================================
#Gavin Day 15/09/16
#Requires a stiffness.csv file with the same filename minus extension and loads in the second column
#change material for to be optimised below
#====================================================================================

import os
import csv
cwd = os.getcwd()
matToOptimise = 'PM_INTERFACE' #Change to whatever material is to be optimised

#template for the python files
template = """# -*- coding: mbcs -*-
import math
import os

def parametrisedTests(scaleFactor):
    from abaqus import mdb
    backwardCompatibility.setValues(reportDeprecated=False)
    from abaqusConstants import ON,THREADS
    fileName = '{currentDir}\{fileName_temp}.inp'
    fileName.replace('/',os.sep)
    myModel = mdb.ModelFromInputFile(inputFileName=fileName, name='model')
    for mat in myModel.materials.keys():
        myMat = myModel.materials[mat]
        if mat.startswith('{matToOpti}'):
            rho = int(myMat.density.table[0][0])
            if rho<1:rho=1
            E = rho*scaleFactor
            nu = 0.3
            del myMat.elastic
            myMat.Elastic(table=((E, nu), ))
    myModel.steps['loading_step'].setValues(nlgeom=ON)
    myJob = mdb.Job(model='model', name='scaledJob')
    myJob.setValues(numCpus=8,numDomains=8,multiprocessingMode=THREADS,scratch='.')
    myJob.writeInput()
    mdb.saveAs(myJob.name)
    return myJob,mdb

def postPro(odbName):
    import sys
    odbToolbox = r"D:\postPro4Abq"
    sys.path.append(odbToolbox)
    print 'running postPro on ',odbName
    import postProTools.odbTools as odbTools
    import postProTools.extractors as ext
    myOdb = odbTools.openOdb(odbName)
    assembly = myOdb.rootAssembly
    time = ext.getTime(myOdb)
    extDispl = ext.getU_3(myOdb, 'REFERENCE_POINT_PLATEN-1        1')
    extDiplsList = [displ[0] for displ in extDispl]
    outForce = ext.getRF_3(myOdb,'REFERENCE_POINT_PLATEN-1        1')
    extForceList = [force[0] for force in outForce]
    stiffness = extForceList[-1]/extDiplsList[-1]*1000.
    odbTools.writeValuesOpti(stiffness)
    myOdb.close()

if __name__ == '__main__':
    import sys
    paramToOpti = float(sys.argv[-1])
    job,mdb = parametrisedTests(paramToOpti)
    try:
        job.submit()
        job.waitForCompletion()
    except:
        pass
    mdb.close()
  """

for filename in os.listdir(cwd): #cycle through files in cwd
    initFile = open('__init__.py','w')
    initFile.close()
    if filename.endswith(".inp"): #find inps
        filename = filename[:-4] #remove extension
        context = {                 #context for the tmplate - bits to change - filname etc.
            "currentDir":cwd,
            "fileName_temp":filename,
            "matToOpti":matToOptimise
        }
        pythonFile = open(filename + '.py', 'w')
        pythonFile.write(template.format(**context))
        pythonFile.close()
        f = open('stiffness.csv') #opens initial stifness.csv
        csv_f = csv.reader(f)
        for row in csv_f:
            if row[0] == filename:
                asciiFile = open(filename + '.ascii', 'w')
                asciiFile.write(str(row[1]))
                asciiFile.close()

        continue
    else:
        continue

