import os
from generator import CodeGenerator 
from assertions import assertType, assertTypeAll
from source import SourceFiles, VariableReference, SubroutineFullName
from capture import CaptureCodeGenerator
from replay import ReplayCodeGenerator
from export import ExportCodeGenerator
from backup import BackupFileFinder
from callgraph import CallGraph
from typefinder import TypeCollection

class CombinedCodeGenerator(CodeGenerator):
    
    def __init__(self, capture, replay, sourceFiles, modifySourceFiles, templatePath, testSourceDir, testDataDir, graphBuilder, postProcessor, backupFinder, settings):
        assertType(capture, 'capture', bool)
        assertType(replay, 'replay', bool)
        assertType(sourceFiles, 'sourceFiles', SourceFiles)
        assertType(modifySourceFiles, 'modifySourceFiles', SourceFiles)
        assertType(templatePath, 'templatePath', str)
        if not os.path.isfile(templatePath):
            raise IOError("Template file not found: " + templatePath)
        assertType(testDataDir, 'testDataDir', str)
        if not os.path.isdir(testDataDir):
            raise IOError("Not a directory: " + testDataDir)
        assertType(backupFinder, 'backupFinder', BackupFileFinder)

        super(CombinedCodeGenerator, self).__init__(sourceFiles, templatePath, graphBuilder, postProcessor, settings)
        self.__modifySourceFiles = modifySourceFiles
        self.__export = ExportCodeGenerator(self._sourceFiles, modifySourceFiles, templatePath, graphBuilder, postProcessor, backupFinder, settings)
        self.__capture = None
        self.__replay = None        
        if capture:
            self.__capture = CaptureCodeGenerator(self._sourceFiles, modifySourceFiles, templatePath, testDataDir, graphBuilder, postProcessor, backupFinder, settings)
        if replay:
            self.__replay = ReplayCodeGenerator(self._sourceFiles, templatePath, testSourceDir, testDataDir, graphBuilder, postProcessor, settings)
    
    def addCode(self, subroutineFullName, typeArgumentReferences, typeResultReferences, globalsReferences, callgraph, types):
        assertType(subroutineFullName, 'subroutineFullName', SubroutineFullName)
        assertTypeAll(typeArgumentReferences, 'typeArgumentReferences', VariableReference)
        assertTypeAll(typeResultReferences, 'typeResultReferences', VariableReference)
        assertTypeAll(globalsReferences, 'globalsReferences', VariableReference)
        assertType(callgraph, 'callgraph', CallGraph)
        assertType(types, 'types', TypeCollection)
        
        self.__export.addCode(subroutineFullName, typeArgumentReferences, typeResultReferences, globalsReferences, callgraph, types)
        if self.__capture:
            self.__modifySourceFiles.clearCache()
            self.__capture.addCode(subroutineFullName, typeArgumentReferences, typeResultReferences, globalsReferences, callgraph, types)
        if self.__replay:
            self.__replay.addCode(subroutineFullName, typeArgumentReferences, typeResultReferences, globalsReferences, callgraph, types)
