import argostranslate.package

argostranslate.package.update_package_index()
available_packages = argostranslate.package.get_available_packages()
pkg = next(p for p in available_packages if p.from_code == "en" and p.to_code == "vi")
argostranslate.package.install_from_path(pkg.download())
print("done")