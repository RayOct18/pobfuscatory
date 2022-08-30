# PyObfuscator

## TODO
- [ ] insert confuse code
- [ ] refactor preserve string function
- [ ] preserve library function (os.path.join, re.fullmatch, ...)
- [x] preserve string (don't replace key in quotes)
- [x] assign value into list (mat_rotation[0][2] += (rotate_w - w) / 2)
- [x] dynamic arguments (*arg, **kwargs)
- [x] star unpack list (a, b, *c, _ = ...)
- [x] multiple line arguments
- [x] preserve specify filename
- [x] open py only
- [x] clean comment
- [x] process files are not belong python
- [x] change these name to random string
    - [x] package
    - [x] file
    - [x] function
    - [x] variable
    - [x] class