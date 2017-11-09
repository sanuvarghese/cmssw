import FWCore.ParameterSet.Config as cms
######
# Configuration to run tau ReReco+PAT at MiniAOD samples
# M. Bluj, NCBJ Warsaw
# based on work of J. Steggemann, CERN
# Created: 9 Nov. 2017
######

######
runSignal=True
#runSignal=False
maxEvents=1000
#maxEvents=-1

# If 'reclusterJets' set true a new collection of uncorrected ak4PFJets is 
# built to seed taus (as at RECO), otherwise standard slimmedJets are used
reclusterJets=True 
#reclusterJets=False

#set true for upgrade studies
phase2=False
#phase2=True

#Output mode
outMode = 0 #store original MiniAOD and new selectedPatTaus 
#outMode = 1 #store original MiniAOD, new selectedPatTaus, and all PFtau products as in AOD (except of unsuported ones)

print 'Running Tau reco&id with MiniAOD inputs:'
print '\t Run on signal:', runSignal
print '\t Recluster jets:', reclusterJets
print '\t Use Phase2 settings:', phase2
print '\t Output mode:', outMode
 
#####
from Configuration.StandardSequences.Eras import eras
era = eras.Run2_2017
if phase2:
	era = eras.Phase2_timing
process = cms.Process("TAURECO",era)
process.load("Configuration.StandardSequences.MagneticField_cff") # for CH reco
if not phase2:
	process.load("Configuration.Geometry.GeometryRecoDB_cff")
else:
	process.load('Configuration.Geometry.GeometryExtended2023D17Reco_cff')

#####
readFiles = cms.untracked.vstring()
secFiles = cms.untracked.vstring() 
process.source = cms.Source ("PoolSource",fileNames = readFiles, secondaryFileNames = secFiles)

process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(maxEvents)
)
print '\t Max events:', process.maxEvents.input.value()

if runSignal:
	f = open("ZTT-validation.txt","r") #opens file with name of "test.txt"
	for file in f.readline():
		readFiles.extend( [ file ] )
	f.close() 
else:
	f = open("QCD-validation.txt","r") #opens file with name of "test.txt"
	for file in f.readline():
		readFiles.extend( [ file ] )
	f.close() 

#####
import RecoTauTag.Configuration.tools.adaptToRunAtMiniAOD as tauAtMiniTools

#####
tauAtMiniTools.addTauReReco(process)

#####
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')
from Configuration.AlCa.GlobalTag import GlobalTag
if not phase2:
	process.GlobalTag = GlobalTag(process.GlobalTag, 'auto:run2_mc', '')
	process.GlobalTag.globaltag = '94X_mc2017_realistic_v1'
else:
	process.GlobalTag = GlobalTag(process.GlobalTag, 'auto:phase2_realistic', '')

#####
#mode = 0: store original MiniAOD and new selectedPatTaus 
#mode = 1: store original MiniAOD, new selectedPatTaus, and all PFtau products as in AOD (except of unsuported ones)
process.output = tauAtMiniTools.setOutputModule(mode=outMode)
if runSignal:
	process.output.fileName='miniAOD_TauReco_ggH.root'
	if reclusterJets:
		process.output.fileName='miniAOD_TauReco_ak4PFJets_ggH.root'
else:
	process.output.fileName='miniAOD_TauReco_QCD.root'
	if reclusterJets:
		process.output.fileName='miniAOD_TauReco_ak4PFJets_QCD.root'
process.out = cms.EndPath(process.output)

#####
tauAtMiniTools.adaptTauToMiniAODReReco(process, reclusterJets)

#####
process.load('FWCore.MessageService.MessageLogger_cfi')
if process.maxEvents.input.value()>10:
     process.MessageLogger.cerr.FwkReport.reportEvery = process.maxEvents.input.value()//10
if process.maxEvents.input.value()>10000 or process.maxEvents.input.value()<0:
     process.MessageLogger.cerr.FwkReport.reportEvery = 1000

#####
process.options = cms.untracked.PSet(
)
process.options.numberOfThreads=cms.untracked.uint32(4)
#process.options.numberOfThreads=cms.untracked.uint32(1)
process.options.numberOfStreams=cms.untracked.uint32(0)
print '\t No. of threads:', process.options.numberOfThreads.value(),', no. of streams:',process.options.numberOfStreams.value()

process.options = cms.untracked.PSet(
     process.options,
     wantSummary = cms.untracked.bool(True)
)
