import argparse
import os
import shutil
import subprocess

ENGINE_GIT_REPO = "git@github.com:Esauidk/GameSmithEngine.git"
DEFAULT_PLATFORM_BUILD = "windows"

def build_game_exec(type, platform, output, redownload=True):
    folder = os.path.abspath("build")
    perform_download = not os.path.exists(folder) or redownload
    if perform_download :   
        print("Creating temp build folder: ", folder)
        os.mkdir(folder)
        subprocess.run(["git", "clone", ENGINE_GIT_REPO, folder], check=True)
        print(os.listdir(folder))
        os.makedirs("%s/third-party/bin/premake" % (folder))
        shutil.copyfile("third-party\\bin\\premake\\premake5.exe", "%s/%s" % (folder, "third-party/bin/premake/premake5.exe"))
    
    wd = os.getcwd()
    os.chdir(folder)
    print(os.listdir())
    subprocess.run(["git", "submodule", "update", "--init"], check=True)
    subprocess.run(["%s/%s" % (folder, "BuildProject.bat")])

    try:
        sln_file = "%s\GameSmithEngineProject.sln" % (folder)
        dll_file = "GameSmithEngine.dll"
        debug_file = "GameSmithEngine.pdb"
        final_binary_location = "%s\\bin\%s-%s-x86_64\GEStandaloneGameApp\GEStandaloneGameApp.exe" % (folder, type.capitalize(), platform)
        final_dll_location = "%s\\bin\%s-%s-x86_64\GameSmithEngine\%s" % (folder, type.capitalize(), platform, dll_file)
        final_dll_debug_location = "%s\\bin\%s-%s-x86_64\GameSmithEngine\%s" % (folder, type.capitalize(), platform, debug_file)
        config = "/p:configuration=%s" % (type)

        print("Compiling game application")
        match platform:
            case "windows":
                subprocess.run(["MSBuild.exe", "/m", config, sln_file], check=True)

        print("Application Compilation Complete!")
        print("Copying Application to: ", output)

        binary_new_location = "%s/%s" % (output, "Test.exe")
        dll_new_location = "%s/%s" % (output, dll_file)
        shutil.copyfile(final_binary_location, binary_new_location)
        shutil.copyfile(final_dll_location, dll_new_location)

        if type == "debug":
            debug_new_location = "%s/%s" % (output, debug_file)
            shutil.copyfile(final_dll_debug_location, debug_new_location)
    finally:
        os.chdir(wd)

def build_prj(prjDir, output):
    folders = ["Assets", "ContentLibraries"]
    for folder in folders:
        path = "%s/%s" % (prjDir, folder)
        outputPath = "%s/%s" % (output, folder)
        if (os.path.isdir(path)) :
            shutil.copytree(path, outputPath)

def parse_args():
    parser = argparse.ArgumentParser("Packages GameSmithEngine Games into standalone playable builds")
    parser.add_argument(
        '-e',
        '--engineVer',
        dest='engineVer',
        required=False,
        default='latest',
        help='The version of the game smith engine to use when compiling the project'
    )

    parser.add_argument(
        '-p',
        '--prj',
        dest='prj',
        required=True,
        help='The path to the directory of the game smith project'
    )

    parser.add_argument(
        '-t',
        '--type',
        dest='type',
        required=False,
        choices=['release', 'debug'],
        default='release',
        help='The game type to build (defaults to release)'
    )

    parser.add_argument(
        '-o',
        '--output',
        dest='output',
        required=True,
        help='The output directory for your game'
    )

    parser.add_argument(
        '-r',
        '--root',
        dest="root",
        required=False,
        default=os.curdir,
        help='The root directory for the build system'
    )

    return parser.parse_args()

def main():
    options = parse_args()
    os.chdir(options.root)

    if (os.path.exists(options.output)):
        print("Removing existing folder:", options.output)
        shutil.rmtree(options.output)

    print("Creating output folder: ", options.output)
    os.mkdir(options.output)

    build_game_exec(options.type, DEFAULT_PLATFORM_BUILD, options.output, False)

    print("Building project into ouput directory")
    build_prj(options.prj, options.output)
    print("Finishing Handling Project Files")

    print("Successful Build!")
    


if __name__ == "__main__":
    main()