"""Gavin Day 15/09/16.

Requires a stiffness.csv file with the same filename minus extension and loads
in the second column change material for to be optimised below.
"""
import os
import csv
cwd = os.getcwd()

# template for the python files
template = """
import os

def parametrisedTests(scaleFactor):
    from abaqus import mdb
    backwardCompatibility.setValues(reportDeprecated=False)
    from abaqusConstants import ON,THREADS
    fileName = r'{currentDir}\{fileName_temp}.inp'
    fileName.replace('/',os.sep)
    myModel = mdb.ModelFromInputFile(inputFileName=fileName, name='model')

    for mat in myModel.materials.keys():
        myMat = myModel.materials[mat]
        if mat.startswith('PMGS'):
            rho = myMat.density.table[0][0]
            E = rho*scaleFactor
            nu = 0.3
            del myMat.elastic
            myMat.Elastic(table=((E, nu), ))

    myJob = mdb.Job(model='model', name='scaledJob')
    myJob.setValues(numDomains=8,
        numCpus=8)
    myJob.writeInput()
    return myJob,mdb

def postPro(odbName):
    odbToolbox = r"D:\GDAY_Opti\HUMAN_INTACT\postPro4Abq"
    import sys
    sys.path.append(odbToolbox)
    import postProTools.odbTools as odbTools
    import postProTools.extractors as ext
    myOdb = odbTools.openOdb(odbName)
    refPoint = 'REFERENCE_POINT_PLATEN-1        1'
    extDispl = ext.getU_3(myOdb, refPoint)
    extDiplsList = [displ[0] for displ in extDispl]
    outForce = ext.getRF_3(myOdb,refPoint)
    extForceList = [force[0] for force in outForce]
    stiffness = extForceList[-1]/extDiplsList[-1]*1000.
    odbTools.writeValuesOpti(stiffness)
    myOdb.close()

if __name__ == '__main__':
    import sys
    optiParam = float(sys.argv[-1])
    job,mdb = parametrisedTests(optiParam)
    job.submit()
    job.waitForCompletion()
    mdb.close()
  """

for filename in os.listdir(cwd):  # cycle through files in cwd
    initFile = open('__init__.py', 'w')
    initFile.close()
    if filename.endswith(".inp"):  # find inps
        filename = filename[:-4]   # remove extension
        context = {                # context for the tmplate - bits to change
                                   # - filname etc.
            "currentDir": cwd,
            "fileName_temp": filename
        }
        pythonFile = open(filename + '.py', 'w')
        pythonFile.write(template.format(**context))
        pythonFile.close()
        f = open('stiffness.csv')  # opens initial stifness.csv
        print('openned stiffness.csv')
        csv_f = csv.reader(f)
        for row in csv_f:
            if row[0] == filename:
                asciiFile = open(filename + '.dat', 'w')
                asciiFile.write(str(row[1]))
                asciiFile.close()

        continue
