import os
from generator import CodeGenerator 
from assertions import assertType
from source import SourceFiles, SourceFile, SubroutineFullName
from templatenamespace import CaptureTemplatesNameSpace
from backup import BackupFileFinder
from linenumbers import LastUseLineFinder

class CaptureCodeGenerator(CodeGenerator):
    
    AFTER_USE_TEMPLATE_PART = 'captureAfterUse'
    BEFORE_CONTAINS_TEMPLATE_PART = 'captureBeforeContains'
    AFTER_LAST_SPECIFICATION_TEMPLATE_PART = 'captureAfterLastSpecification'
    BEFORE_END_TEMPLATE_PART = 'captureBeforeEnd'
    AFTER_LAST_LINE_TEMPLATE_PART = 'captureAfterSubroutine'
    EXPORT_TEMPLATE_PART = 'export'
    
    def __init__(self, sourceFiles, modifySourceFiles, templatePath, testDataDir, graphBuilder, backupFinder, excludeModules = [], ignoredModulesForGlobals = [], ignoredTypes = [], ignoreRegex = ''):
        assertType(sourceFiles, 'sourceFiles', SourceFiles)
        assertType(templatePath, 'templatePath', str)
        if not os.path.isfile(templatePath):
            raise IOError("Template file not found: " + templatePath)
        assertType(testDataDir, 'testDataDir', str)
        if not os.path.isdir(testDataDir):
            raise IOError("Not a directory: " + testDataDir)
        assertType(backupFinder, 'backupFinder', BackupFileFinder)

        super(CaptureCodeGenerator, self).__init__(sourceFiles, templatePath, graphBuilder, excludeModules, ignoredModulesForGlobals, ignoredTypes, ignoreRegex)
        self.__modifySourceFiles = modifySourceFiles      
        self.__testDataDir = testDataDir     
        self.__backupFinder = backupFinder

    def addCode(self, subroutine, typeArgumentReferences, typeResultReferences, globalsReferences):
        print "  Add Code to Module under Test"
        
        originalSourceFile = subroutine.getSourceFile()
        sourceFilePath = originalSourceFile.getPath()
        if sourceFilePath.endswith(self.__backupFinder.getBackupSuffix()):
            sourceFilePath = sourceFilePath.replace(self.__backupFinder.getBackupSuffix(), CodeGenerator.DEFAULT_SUFFIX)
            subroutine = SourceFile(sourceFilePath, originalSourceFile.isPreprocessed()).getSubroutine(subroutine.getName())
        
        self.__backupFinder.setBackupSuffixPrefix(BackupFileFinder.CAPTURE_SUFFIX_PREFIX)            
        self.__backupFinder.create(sourceFilePath)
        templateNameSpace = CaptureTemplatesNameSpace(subroutine, typeArgumentReferences, typeResultReferences, globalsReferences, self.__testDataDir)
        # Reihenfolge wichtig: von unten nach oben!!!
        self._processTemplate(sourceFilePath, subroutine.getLastLineNumber(), self.AFTER_LAST_LINE_TEMPLATE_PART, templateNameSpace)
        lastLine = subroutine.getContainsLineNumber()
        if lastLine < 0:
            lastLine = subroutine.getLastLineNumber()
        self._processTemplate(sourceFilePath, lastLine - 1, self.BEFORE_END_TEMPLATE_PART, templateNameSpace)
        lastSpecificationLineNumber = subroutine.getLastSpecificationLineNumber()
        lastSpecificationLineNumber = self.__shiftLineNumberByPreprocesserorEndifs(subroutine, lastSpecificationLineNumber)
        self._processTemplate(sourceFilePath, lastSpecificationLineNumber, self.AFTER_LAST_SPECIFICATION_TEMPLATE_PART, templateNameSpace)
        self._processTemplate(sourceFilePath, subroutine.getModule().getContainsLineNumber() - 1, self.BEFORE_CONTAINS_TEMPLATE_PART, templateNameSpace)
        lastUseLineNumber = subroutine.getModule().getLastUseLineNumber()
        lastUseLineNumber = self.__shiftLineNumberByPreprocesserorEndifs(subroutine.getModule(), lastUseLineNumber)
        self._processTemplate(sourceFilePath, lastUseLineNumber, self.AFTER_USE_TEMPLATE_PART, templateNameSpace)

    def _findSubroutine(self, subroutineFullName):
        assertType(subroutineFullName, 'subroutineFullName', SubroutineFullName)
        
        return self.__modifySourceFiles.findSubroutine(subroutineFullName)
    
    def __extractModulesFromVariableReferences(self, references):
        modules = set()
        for ref in references:
            declaredIn = ref.getDeclaredIn() 
            if declaredIn is not None:
                module = declaredIn.getModule()
                if module is not None:
                    if self.__modifySourceFiles != self._sourceFiles:
                        module = self.__modifySourceFiles.findModule(module.getName())
                    if module is not None:
                        modules.add(module)
        
        return modules
    
    def __shiftLineNumberByPreprocesserorEndifs(self, subroutine, fromLineNumber):
        found = False
        toLineNumber = -1
        for i, _, j in subroutine.getStatements():
            if found:
                toLineNumber = i
                break
            elif j >= fromLineNumber:
                found = True
                toLineNumber = j
        
        shiftedLineNumber = fromLineNumber
        for lineNumber in range(fromLineNumber, toLineNumber):
            line = subroutine.getLine(lineNumber)
            if line.strip() == '#endif':
                shiftedLineNumber = lineNumber
                
        return shiftedLineNumber
