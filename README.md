# FortranTestGenerator

`FortranTestGenerator` (FTG) is a tool for automatically generating unit tests for subroutines of existing Fortran applications based on an approach called Capture & Replay.

One of the main effort for creating unit tests is the set-up of consistent input data. When working with legacy code, we can make use of the existing infrastructure and extract test data from the running application. 
FTG generates code for serializing and storing a subroutines input data and inserts this code temporarily into the subroutine (capture code).
In addition, FTG generates a basic test driver which loads this data and runs the subroutine (replay code). 
Meaningful checks and test data modification needs to be added by the developer.
All the code generated by FTG is based on customizable templates. So you are able to adapt it to your software environment.

FTG is written in Python and the principles of FTG are described in the following paper:

> C. Hovy and J. Kunkel, "Towards Automatic and Flexible Unit Test Generation for Legacy HPC Code," *2016 Fourth International Workshop on Software Engineering for High Performance Computing in Computational Science and Engineering (SE-HPCCSE)*, Salt Lake City, UT, 2016, pp. 1-8.
> http://dx.doi.org/10.1109/SE-HPCCSE.2016.005

So far, the documentation is not complete. If your interested in using `FortranTestGenerator`, please feel free to contact me:   
Christian Hovy <<hovy@informatik.uni-hamburg.de>>

## In general it works as follows

1. You identify an existing subroutine in your Fortran application and a certain execution of this subroutine that you want to run for test purposes in isolation, that is without the surrounding application.

2. You run FTG to insert the capture code into the subroutine. This code is responsible for storing all input variables to you hard drive when the capturing is active. Thanks to a built-in static source code analysis, only those variable are captured that are actually needed by the subroutine or by one of its directly or indirectly called routines.

3. Then you define the event on which the capturing should take place. By default, it's the first execution of the subroutine.

4. You compile and run your application with the capture code.

5. You run FTG to create the replay code, that means a basis test driver which loads the captured data and calls the subroutine by passing the captured data as input.

Variables that are considered to be input data:
* Arguments of intrisic types
* Components of derived type arguments that are actually used by the subroutine
* Module variables of the same module or imported by USE statements that are actually used by the subroutine

For the source code analysis, FTG uses the tool [FortranCallgraph](https://github.com/chovy1/fortrancallgraph), which needs assembler files generated by [gfortran](https://gcc.gnu.org/fortran) for the analysis.

## Prerequisites 

To run FTG, you will need the following software packages:

* `Python 2.7` (Python 3+ is currently not supported, but all uncompatible stuff will be removed in the future)
* The `Cheetah Template Engine`: https://github.com/cheetahtemplate/cheetah (Unfortunately, development and support here has stopped during the development of FTG, but there is now a fork on: https://github.com/CheetahTemplate3/cheetah3, which has not yet been tested with FTG though.)
* This modified version of the `SerialBox` library: https://github.com/chovy1/serialbox
* `FortranCallgraph`: https://github.com/chovy1/fortrancallgraph

## Quick Start Guide

#### 1. Get and install `SerialBox`
... from here: https://github.com/chovy1/serialbox and learn how to built your application with it. 

#### 2. Get and install the `Cheetah Template Engine`
...from here: https://github.com/cheetahtemplate/cheetah or here: https://github.com/CheetahTemplate3/cheetah3 or just look if your OS provides a package (e.g. Ubuntu does).

#### 3. Get `FortranCallgraph` 
...from here: https://github.com/chovy1/fortrancallgraph

#### 4. Configure and try `FortranCallgraph`
...according to its [documentation](https://github.com/chovy1/fortrancallgraph/blob/master/README.md).

#### 5. Clone this repo

```
$> git clone https://github.com/chovy1/fortrantestgenerator.git
$> cd fortrantestgenerator
```

#### 6. Fill out the configuration file [config_fortrantestgenerator.py](config_fortrantestgenerator.py)

`FTG_DIR` : The location of FortranTestGenerator (usually `os.path.dirname(os.path.realpath(__file__))`)

`FCG_DIR` : The location of FortranCallgraph (usually `FTG_DIR + '../fortrancallgraph'')

`TEMPLATE_DIR` : The location of the templates to be used for code generation (`FTG_DIR + '/templates/standalone_nompi'` shall be a good start, or `FTG_DIR + '/templates/standalone'` if your application uses MPI)

`TEST_SOURCE_DIR` : The folder where the generated test driver shall be put in.

`TEST_DATA_BASE_DIR` : The folder where the captured data shall be put in.

**Please note:** If you don't want to have the configuration spread over the two files of FortranCallgraph and FortranTestGenerator, you can put all the variables from config_fortrancallgraph.py into config_fortrantestgenerator.py instead of importing them.

#### 7. Create assembler files

Compile your Fortran application with [gfortran](https://gcc.gnu.org/fortran) and the options `-S -g -O0` to generate assembler files.

#### 8. Create capture code

Let's assume your subtroutine under test is the subroutine `my_subroutine` from the module `my_module`. Just run:

```
$> ./FortranTestgenerator.py -c my_module my_subroutine
```
#### 9. Define capture event

Have a look at the generated code in the module file where the subroutine under test (`my_subroutine`) is located.
When using one of the provided templates, there are now the two functions: `ftg_my_subroutine_capture_input_active` and `ftg_my_subroutine_capture_output_active`. Those functions define when the time is come to capture the subroutines' input and output. 

By default, both functions just compare the variable `ftg_velocity_tendencies_round`, in which the subroutine executions are counted, with the variable `ftg_velocity_tendencies_capture_round`. By default, `ftg_velocity_tendencies_capture_round` is set to `1`, which means that the capturing takes place in the first execution of `my_subroutine`.

If you want the capturing to happen for example in the 42nd execution of `my_subroutine`, just set `ftg_velocity_tendencies_capture_round` to `42`, but you can also change the functions to what ever you like. If you want to make the time for capturing dependent on the status of another variable, you can also add arguments to those functions. Of course, then you need to add the arguments also at the places where the functions are called.

#### 10. Create folders for the captured data

You will need the following directories for capturing data from `my_subroutine`:
* `TEST_DATA_BASE_DIR/ftg_my_subroutine_test/input`
* `TEST_DATA_BASE_DIR/ftg_my_subroutine_test/output`
* `TEST_DATA_BASE_DIR/ftg_my_subroutine_test/output_test`

`TEST_DATA_BASE_DIR` stands for the path set in the configuration file. `my_subroutine` has to be replaced by the actual subroutine name.

It is a little bit annoying that you have to create these folders manually, but currently there is no other option.

#### 11. Compile and run your application with the capture code

This will only work if you have added the includes and libraries of SerialBox to your build configuration, see step 1.

When the capturing is taking place, there will be messages printed to `stdout` beginning with `FTG...`.

When each MPI process has printed `FTG FINALIZE OUTPUT DATA my_subroutine`, capturing has finished and you can kill your application.

#### 12. Create replay code
Run:
```
$> ./FortranTestgenerator.py -r my_module my_subroutine
```
#### 13. Compile and run the generated test driver (replay code)

You have to run the test with the same numbers of MPI processes as you have done for capturing.

#### 14. Compare the original output with the output from the test

The original output is located in `TEST_DATA_BASE_DIR/ftg_my_subroutine_test/output` and the test output was put into `TEST_DATA_BASE_DIR/ftg_my_subroutine_test/output_test`.

To compare the data, you can use `serialbox-compare`: https://github.com/chovy1/serialbox-compare.

Do the following:
```
$> cd TEST_DATA_BASE_DIR/ftg_my_subroutine_test
$> sbcompare output/ftg_my_subroutine_output_0.json output_test/ftg_my_subroutine_output_0.json
```
This compares the output for the first MPI process. Replace `_0` by `_1`, `_2`, etc. for comparing the output of the other processes. 

If deviations are shown, it's up to you to figure out what went wrong, for example if one variable was missed by the source code analysis or if there is some kind of non-determinism in your code.

#### 15. Make a real test out of the generated test driver

For example add some checks, modify the loaded input data and run the subroutine under test again etc.

You should also remove the dependencies to the capture code, so that you can remove that stuff from the subroutine and its module.

If you want to load the original output data for your checks, just have a look how this is done for the input data.

Some basic checks will be added to the provided templates in the future.

## Please Note

* `FortranTestGenerator.py -c` not only generates the capture code in the module with the subroutine under test, but also a `PUBLIC` statements in every module that contains a module variable that is needed by the test and not yet public (export code).
This only works for module variables that are private because the whole module is private and they are not explicitly set to public. If a variable is private because it has the private keyword in its declaration, this procedure won't work and you have to manually make them public. The compiler will tell you if there is such a problem. Similar problems can occure elsewhere.

* For each module that is modified by `FortranTestGenerator.py -c` a copy of the original version is created with the file ending `.ftg-backup`. You can restore these backups by running
  ```
  $> ./FortranTestGenerator.py -b
  ```
* You can combine the options `-b`, `-c` and `-r` in any combination. When running `FortranTestGenerator.py` with `-b` option, restoring the backups will always be the first action, and when running with `-r`, generating the replay code will come at last.

* `-b` will restore all backups, so also the generated PUBLIC statements will be removed, but usually, you will need them for your test. So, if you want any generated code to stay, just remove the corresponding .ftg-backup file. It then might make sense to add some preprocessor directives around the generated code (e.g. something like `#ifdef __FTG_TESTS_ENABLED__ ... #endif`). If you want to have such directives always be there, just add them to the template you are using.

* As long as there is a backup file, any analysis is done on this instead of the original file.

* As mentioned before, the static source code analysis is done by [FortranCallgraph](https://github.com/chovy1/fortrancallgraph) which combines an analysis of assembler files with an analysis of the original source code. Actually, it first creates a call graph with the subroutine under test as root by parsing the assembler files and then it traverses this call graph while analysing the original (unpreprocessed) source files. This procedure can lead to problems if your code contains too much preprocessor acrobatics. 

  And there are also other cases where the assembler code differs from the orginal source code. Example:
  ```fortran
  LOGICAL, PARAMETER check = .TRUE.
  IF (check) THEN
    CALL a()
  ELSE
    CALL b()
  END IF
  ```
  Even when compiled with `-O0`, the `ELSE` block in this example won't be in the assembler/binary code. But usually this is not a problem, there will just be a warning during the analysis that the subroutine `b` is not found in the call graph.
  
* When you change your code, you will have to compile again with `-S -g -O0` to generate new assembler files. For example, when you have generated capture and export code and removed some backup files to make the code permanent, you have to compile again.

* The static source code analysis has the same limitations as every static analysis, it can only find out what can be found out by parsing the source code. So mainly, it can not handle runtime polymorphism. That means, the use of, for example, function pointers or inheritance can lead to wrong results.

* If any problem occurs, please feel free to contact me:   
Christian Hovy <<hovy@informatik.uni-hamburg.de>>

## Modifying the templates

The templates are based on the `Cheetah Template Engine` and an API which has no documentation so far. Please ask me, if you need help with adapting the generated code to your needs:   
Christian Hovy <<hovy@informatik.uni-hamburg.de>>

## Notes for ICON developers

#### 1. Building ICON with SerialBox

* For including the libraries, you can just use the `OTHER_LIBS` variable in your `mh-linux` file:
  ```
  OTHER_LIBS  = ${OTHER_LIBS} -L${SERIALBOX_ROOT}/lib -lFortranSer -lSerialBoxWrapper -lSerialBox -lUtils -ljson -lstdc++ -lsha256
  ```
* For including the includes, there is no such variable, so I have just addded them to the `FFLAGS` variable:
  ```
  FFLAGS = ${FFLAGS} -I${SERIALBOX_ROOT}/include/fortran
  ```

#### 2. Create assembler files

I have done it like this:

* In my `mh-linux` file I have added `$FFLAGS` itself to `FFLAGS` under the `gcc` section:
  ```
  FFLAGS      = $FFLAGS $FCPP $FLANG $FWARN $INCLUDES
  ```
* Then, when I want to create the assembler files, I just run:
  ```
  $> export FFLAGS='-S -g -O0'
  $> ./configure
  $> rm build/x86_64-unknown-linux-gnu/src/*.o
  $> make
  $> export FFLAGS=
  ```
  `make` will end up with an error, that an `*.o` file is missing, but that's fine.

#### 3. Compiling the tests
  
* When using the `icon_standalone` template, just put the generated test files into the `src/tests` directory, see step 6 in the Quick Start Guide:
  ```
  TEST_SOURCE_DIR = '<iconroot>/src/tests'
  ```
  `./configure` will then automatically add the test to the `Makefile` and you will get a binary in `build/.../bin`.
* You can also generate tests for the *testbed* by using the `icon_testbed` templates, but this will be a bit more complicated. You will then have to integrate the generated modules manually into the testbed environment and create proper run scripts.

#### 4. Configuration of FortranCallgraph

The following configuration has shown to work pretty well:

```
ASSEMBLER_DIR = '<iconroot>/build/x86_64-unknown-linux-gnu/src'
SOURCE_DIR = '<iconroot>/src'

SPECIAL_MODULE_FILES = {'mo_mcrph_sb': 'mo_2mom_mcrph_driver.f90',
                        'mo_lrtm': 'mo_lrtm_driver.f90', 'ppm_extents': 'mo_extents.f90',
                        'psrad_rrsw_kg16': 'mo_psrad_srtm_kgs.f90', 'psrad_rrsw_kg17': 'mo_psrad_srtm_kgs.f90', 
                        'psrad_rrsw_kg18': 'mo_psrad_srtm_kgs.f90', 'psrad_rrsw_kg19': 'mo_psrad_srtm_kgs.f90', 
                        'psrad_rrsw_kg20': 'mo_psrad_srtm_kgs.f90', 'psrad_rrsw_kg21': 'mo_psrad_srtm_kgs.f90', 
                        'psrad_rrsw_kg22': 'mo_psrad_srtm_kgs.f90', 'psrad_rrsw_kg23': 'mo_psrad_srtm_kgs.f90', 
                        'psrad_rrsw_kg24': 'mo_psrad_srtm_kgs.f90', 'psrad_rrsw_kg25': 'mo_psrad_srtm_kgs.f90', 
                        'psrad_rrsw_kg26': 'mo_psrad_srtm_kgs.f90', 'psrad_rrsw_kg27': 'mo_psrad_srtm_kgs.f90', 
                        'psrad_rrsw_kg28': 'mo_psrad_srtm_kgs.f90', 'psrad_rrsw_kg29': 'mo_psrad_srtm_kgs.f90', 
                        'rrlw_planck': 'mo_psrad_lrtm_kgs.f90', 'psrad_rrlw_kg01': 'mo_psrad_lrtm_kgs.f90', 
                        'psrad_rrlw_kg02': 'mo_psrad_lrtm_kgs.f90', 'psrad_rrlw_kg03': 'mo_psrad_lrtm_kgs.f90', 
                        'psrad_rrlw_kg04': 'mo_psrad_lrtm_kgs.f90', 'psrad_rrlw_kg05': 'mo_psrad_lrtm_kgs.f90', 
                        'psrad_rrlw_kg06': 'mo_psrad_lrtm_kgs.f90', 'psrad_rrlw_kg07': 'mo_psrad_lrtm_kgs.f90', 
                        'psrad_rrlw_kg08': 'mo_psrad_lrtm_kgs.f90', 'psrad_rrlw_kg09': 'mo_psrad_lrtm_kgs.f90', 
                        'psrad_rrlw_kg10': 'mo_psrad_lrtm_kgs.f90', 'psrad_rrlw_kg11': 'mo_psrad_lrtm_kgs.f90', 
                        'psrad_rrlw_kg12': 'mo_psrad_lrtm_kgs.f90', 'psrad_rrlw_kg13': 'mo_psrad_lrtm_kgs.f90', 
                        'psrad_rrlw_kg14': 'mo_psrad_lrtm_kgs.f90', 'psrad_rrlw_kg15': 'mo_psrad_lrtm_kgs.f90', 
                        'psrad_rrlw_kg16': 'mo_psrad_lrtm_kgs.f90', 
                        'rrlw_kg01': 'mo_lrtm_kgs.f90', 'rrlw_kg02': 'mo_lrtm_kgs.f90', 
                        'rrlw_kg03': 'mo_lrtm_kgs.f90', 'rrlw_kg04': 'mo_lrtm_kgs.f90', 
                        'rrlw_kg05': 'mo_lrtm_kgs.f90', 'rrlw_kg06': 'mo_lrtm_kgs.f90', 
                        'rrlw_kg07': 'mo_lrtm_kgs.f90', 'rrlw_kg08': 'mo_lrtm_kgs.f90', 
                        'rrlw_kg09': 'mo_lrtm_kgs.f90', 'rrlw_kg10': 'mo_lrtm_kgs.f90', 
                        'rrlw_kg11': 'mo_lrtm_kgs.f90', 'rrlw_kg12': 'mo_lrtm_kgs.f90', 
                        'rrlw_kg13': 'mo_lrtm_kgs.f90', 'rrlw_kg14': 'mo_lrtm_kgs.f90', 
                        'rrlw_kg15': 'mo_lrtm_kgs.f90', 'rrlw_kg16': 'mo_lrtm_kgs.f90', 
                        'yoesrta16': 'mo_srtm_kgs.f90', 'yoesrta17': 'mo_srtm_kgs.f90', 
                        'yoesrta18': 'mo_srtm_kgs.f90', 'yoesrta19': 'mo_srtm_kgs.f90', 
                        'yoesrta20': 'mo_srtm_kgs.f90', 'yoesrta21': 'mo_srtm_kgs.f90', 
                        'yoesrta22': 'mo_srtm_kgs.f90', 'yoesrta23': 'mo_srtm_kgs.f90', 
                        'yoesrta24': 'mo_srtm_kgs.f90', 'yoesrta25': 'mo_srtm_kgs.f90', 
                        'yoesrta26': 'mo_srtm_kgs.f90', 'yoesrta27': 'mo_srtm_kgs.f90', 
                        'yoesrta28': 'mo_srtm_kgs.f90', 'yoesrta29': 'mo_srtm_kgs.f90'}

EXCLUDE_MODULES = ['mpi', 'omp_lib', 'mo_io_units', 'mo_utilities', 'iso_c_binding', 
                   'mod_prism_proto', 'ifcore', 'mo_cdi', 'mo_control', 'mo_submodel',
                   'mtime', 'sct', 'ppm_distributed_array', 'data_parameters',
                   'data_constants', 'data_runcontrol', 'data_modelconfig', 'data_fields',
                   'data_parallel', 'data_soil', 'turbulence_data', 'data_1d_global',
                   'mo_art_nml', 'mo_art_init_interface', 'mo_art_emission_interface', 
                   'mo_art_washout_interface', 'mo_art_diagnostics_interface', 
                   'mo_art_reaction_interface', 'mo_art_clouds_interface', 
                   'mo_art_radiation_interface', 'mo_art_turbdiff_interface', 
                   'mo_art_sedimentation_interface', 'mo_art_tools_interface', 
                   'mo_art_tracer_interface', 'mo_art_config']

IGNORE_GLOBALS_FROM_MODULES = EXCLUDE_MODULES + ['mo_mpi'] 

IGNORE_DERIVED_TYPES = []
```

## License

[GNU General Public License v3.0](LICENSE)
