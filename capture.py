import os
from generator import CodeGenerator 
from utils import assertType
from source import SourceFiles
from templatenamespace import CaptureTemplatesNameSpace, ExportNameSpace

class CaptureCodeGenerator(CodeGenerator):
    
    AFTER_LAST_LINE_TEMPLATE = 'capture.aftersubroutine.tmpl'
    BEFORE_CONTAINS_TEMPLATE = 'capture.beforecontains.tmpl'
    AFTER_LAST_USE_TEMPLATE = 'capture.afterlastuse.tmpl'
    AFTER_LAST_SPECIFICATION_TEMPLATE = 'capture.afterlastspecification.tmpl'
    BEFORE_END_TEMPLATE = 'capture.beforeend.tmpl'
    EXPORT_TEMPLATE = 'export.beforecontains.tmpl'
    
    def __init__(self, sourceFiles, templateDir, testDataDir, graphBuilder, backupSuffix, excludeModules = [], ignoredModulesForGlobals = [], ignoredTypes = [], ignoreRegex = ''):
        assertType(sourceFiles, 'sourceFiles', SourceFiles)
        assertType(templateDir, 'templateDir', str)
        if not os.path.isdir(templateDir):
            raise IOError("Not a directory: " + templateDir);
        assertType(testDataDir, 'testDataDir', str)
        if not os.path.isdir(testDataDir):
            raise IOError("Not a directory: " + testDataDir);

        super(CaptureCodeGenerator, self).__init__(sourceFiles, graphBuilder, backupSuffix, excludeModules, ignoredModulesForGlobals, ignoredTypes, ignoreRegex)
        
        self.__afterLastLineTemplate = templateDir + '/' + self.AFTER_LAST_LINE_TEMPLATE
        self.__beforeContainsTemplate = templateDir + '/' + self.BEFORE_CONTAINS_TEMPLATE
        self.__afterLastUseTemplate = templateDir + '/' + self.AFTER_LAST_USE_TEMPLATE
        self.__afterLastSpecificationTemplate = templateDir + '/' + self.AFTER_LAST_SPECIFICATION_TEMPLATE
        self.__beforeEndTemplate = templateDir + '/' + self.BEFORE_END_TEMPLATE
        self.__exportTemplate = templateDir + '/' + self.EXPORT_TEMPLATE
        
        self.__testDataDir = testDataDir

        
    def _addCode(self, subroutine, typeArgumentReferences, globalsReferences):
        print "  Add Code"
        
        sourceFilePath = subroutine.getSourceFile().getPath()
        
        print "    ...to Module under Test"
        self._createFileBackup(sourceFilePath)
        templateNameSpace = CaptureTemplatesNameSpace(subroutine, typeArgumentReferences, globalsReferences, self.__testDataDir)
        # Reihenfolge wichtig: von unten nach oben!!!
        self._processTemplate(sourceFilePath, subroutine.getLastLineNumber() + 1, self.__afterLastLineTemplate, templateNameSpace)
        lastLine = subroutine.getContainsLineNumber()
        if lastLine < 0:
            lastLine = subroutine.getLastLineNumber()
        self._processTemplate(sourceFilePath, lastLine - 1, self.__beforeEndTemplate, templateNameSpace)
        self._processTemplate(sourceFilePath, subroutine.getLastSpecificationLineNumber() + 1, self.__afterLastSpecificationTemplate, templateNameSpace)
        self._processTemplate(sourceFilePath, subroutine.getModule().getContainsLineNumber() - 1, self.__beforeContainsTemplate, templateNameSpace)
        
        print "    ...to Used Modules"
        moduleName = subroutine.getModuleName()
        for refModule in self._extractModulesFromVariableReferences(globalsReferences):
            if refModule != moduleName:
                usedSourceFile = self._findSourceFileForModule(refModule)
                if not usedSourceFile.isPublic():
                    usedSourceFilePath = usedSourceFile.getPath()
                    backup = self._createFileBackup(usedSourceFilePath)
                    exportTemplateNameSpace = ExportNameSpace(refModule, usedSourceFile, globalsReferences)
                    result = self._processTemplate(usedSourceFilePath, usedSourceFile.getContainsLineNumber() - 1, self.__exportTemplate, exportTemplateNameSpace)
                    if backup and not result:
                        self._removeFileBackup(usedSourceFilePath)
        
