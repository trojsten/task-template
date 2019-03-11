MAKEFLAGS += --no-builtin-rules

.SECONDEXPANSION:

input/seminar/format-root.tex: \
	modules/seminar/format/format-root.tex \
	source/seminar/meta.yaml
	@mkdir -p $(dir $@)
	python3 ./modules/seminar/build/format.py 'source/seminar/' 'modules/seminar' -o '$(dir $@)'

input/seminar/%/format-competition.tex: \
	modules/seminar/format/format-competition.tex \
	input/seminar/format-root.tex \
	input/seminar/$$*/copy-static \
	source/seminar/$$*/meta.yaml
	$(eval words := $(subst /, ,$*))
	@mkdir -p $(dir $@)
	python3 ./modules/seminar/build/format.py 'source/seminar/' 'modules/seminar' -c $(word 1,$(words)) -o '$(dir $@)'

input/seminar/%/format-volume.tex: \
	modules/seminar/format/format-volume.tex \
	source/seminar/$$*/meta.yaml \
	$$(subst $(cdir),,$$(abspath input/seminar/$$*/../format-competition.tex))
	$(eval words := $(subst /, ,$*))
	@mkdir -p $(dir $@)
	python3 ./modules/seminar/build/format.py 'source/seminar/' 'modules/seminar' -c $(word 1,$(words)) -v $(word 2,$(words)) -o '$(dir $@)'

input/seminar/%/format-semester.tex: \
	modules/seminar/format/format-semester.tex \
	source/seminar/$$*/meta.yaml \
	$$(subst $(cdir),,$$(abspath input/seminar/$$*/../format-volume.tex))
	$(eval words := $(subst /, ,$*))
	@mkdir -p $(dir $@)
	python3 ./modules/seminar/build/format.py 'source/seminar/' 'modules/seminar' -c $(word 1,$(words)) -v $(word 2,$(words)) -s $(word 3,$(words)) -o '$(dir $@)'

input/seminar/%/format-round.tex: \
	modules/seminar/format/format-round.tex \
	source/seminar/$$*/meta.yaml \
	$$(subst $(cdir),,$$(abspath input/seminar/$$*/../format-semester.tex))
	$(eval words := $(subst /, ,$*))
	@mkdir -p $(dir $@)
	python3 ./modules/seminar/build/format.py 'source/seminar/' 'modules/seminar' -c $(word 1,$(words)) -v $(word 2,$(words)) -s $(word 3,$(words)) -r $(word 4,$(words)) -o '$(dir $@)'

input/seminar/%/copy-static:
	@mkdir -p $(dir $@)static/
	cp -r source/seminar/$*/static/ input/seminar/$*/

input/seminar/%/intro.tex input/seminar/%/rules.tex: \
	$$(subst $(cdir),,$$(abspath modules/seminar/templates/$$(notdir $$@)))
	$(eval words := $(subst /, ,$*))
	@mkdir -p $(dir $@)
	python3 ./modules/seminar/build/semester.py 'source/seminar/' 'modules/seminar' $(word 1,$(words)) $(word 2,$(words)) $(word 3,$(words)) -o '$(dir $@)'

input/seminar/%/problems.tex input/seminar/%/solutions.tex: \
	input/seminar/$$*/format-round.tex \
	$$(wildcard source/seminar/$$*/*/meta.yaml) \
	source/seminar/$$*/meta.yaml
	$(eval words := $(subst /, ,$*))
	@mkdir -p $(dir $@)
	python3 ./modules/seminar/build/round.py 'source/seminar/' 'modules/seminar' -c $(word 1,$(words)) -v $(word 2,$(words)) -s $(word 3,$(words)) -r $(word 4,$(words)) -o '$(dir $@)'

#input/seminar/%/semester.tex: \
#	input/seminar/$$*/format/semester.tex \
#	input/seminar/$$*/intro.tex \
#	input/seminar/$$*/rules.tex \
#	$$(wildcard source/seminar/$$*/*/*/meta.yaml) \
#	$$(wildcard source/seminar/$$*/*/meta.yaml) \
#	$$(foreach dir,$$(dir $$(subst source/,input/,$$(wildcard source/seminar/$$*/*/meta.yaml))), $$(dir)format/format-round.tex) \
#	source/seminar/$$*/meta.yaml \
#	modules/seminar/styles/$$(word 1, $$(subst /, ,$$*))/templates/intro.tex \
#	modules/seminar/styles/$$(word 1, $$(subst /, ,$$*))/templates/rules.tex 
#	$(eval words := $(subst /, ,$*))
#	@mkdir -p $(dir $@)
#	python3 ./modules/seminar/build-semester.py 'source/seminar/' 'modules/seminar' $(word 1,$(words)) $(word 2,$(words)) $(word 3,$(words)) -o '$(dir $@)'
#
#input/seminar/%/invite.tex: \
#	modules/seminar/templates/invite.tex \
#	input/seminar/$$*/format/semester.tex \
#	source/seminar/$$*/meta.yaml
#	$(eval words := $(subst /, ,$*))
#	@mkdir -p $(dir $@)
#	python3 modules/seminar/build-invite.py 'source/seminar/' 'modules/seminar' $(word 1,$(words)) $(word 2,$(words)) $(word 3,$(words)) -o '$(dir $@)'

input/seminar/%/pdf-prerequisites: \
	$$(subst source/,input/,$$(wildcard source/seminar/$$*/*/*.jpg)) \
	$$(subst source/,input/,$$(wildcard source/seminar/$$*/*/*.png)) \
	$$(subst source/,input/,$$(subst .svg,.pdf,$$(wildcard source/seminar/$$*/*/*.svg))) \
	$$(subst source/,input/,$$(subst .gp,.pdf,$$(wildcard source/seminar/$$*/*/*.gp))) \
	$$(wildcard source/seminar/$$*/*/meta.yaml) \
	source/seminar/$$*/meta.yaml ;

output/seminar/%/html-prerequisites: \
	$$(subst source/,output/,$$(wildcard source/seminar/$$*/*/*.jpg)) \
	$$(subst source/,output/,$$(wildcard source/seminar/$$*/*/*.png)) \
	$$(subst source/,output/,$$(subst .svg,.png,$$(wildcard source/seminar/$$*/*/*.svg))) \
	$$(subst source/,output/,$$(subst .gp,.png,$$(wildcard source/seminar/$$*/*/*.gp))) ;

output/seminar/%/problems.pdf: \
	$$(subst source/,input/,$$(subst .md,.tex,$$(wildcard source/seminar/$$*/*/problem.md))) \
	input/seminar/%/pdf-prerequisites \
	input/seminar/%/problems.tex
	$(call doubletex,seminar)

output/seminar/%/solutions.pdf: \
	$$(subst source/,input/,$$(subst .md,.tex,$$(wildcard source/seminar/$$*/*/solution.md))) \
	input/seminar/%/pdf-prerequisites \
	input/seminar/%/solutions.tex
	$(call doubletex,seminar)

output/seminar/%/semester.pdf: \
	$$(subst source/,input/,$$(subst .md,.tex,$$(wildcard source/seminar/$$*/*/*/problem.md))) \
	input/seminar/%/*/pdf-prerequisites \
	input/seminar/%/semester.tex
	$(call doubletex,seminar)

output/seminar/%/semester-print.pdf: \
	output/seminar/%/semester.pdf
	@echo -e '$(c_action)Converting $(c_filename)$<$(c_action) to a short-edge booklet $(c_filename)$@$(c_action):$(c_default)'
	pdfbook --short-edge --quiet --outfile $@ $<

output/seminar/%/html-problems: \
	output/seminar/%/html-prerequisites \
	$$(subst source/,output/,$$(subst .md,.html,$$(wildcard source/seminar/$$*/*/problem.md))) ;
	
output/seminar/%/html-solutions:\
	output/seminar/%/html-prerequisites \
	$$(subst source/,output/,$$(subst .md,.html,$$(wildcard source/seminar/$$*/*/solution.md))) ;

output/seminar/%/pdf: \
	output/seminar/%/problems.pdf \
	output/seminar/%/solutions.pdf ;

output/seminar/%/html: \
	output/seminar/%/html-problems \
	output/seminar/%/html-solutions ;

output/seminar/%/problems: \
	output/seminar/%/problems.pdf \
	output/seminar/%/html-problems ;

output/seminar/%/solutions: \
	output/seminar/%/solutions.pdf \
	output/seminar/%/html-solutions ;

output/seminar/%: \
	output/seminar/%/problems \
	output/seminar/%/solutions ;

output/seminar/%/invite.pdf:\
	input/$$*/invite.tex\
	source/%/meta.yaml
	$(call doubletex,seminar)

.PHONY:

output/seminar/%/copy: \
	output/seminar/%/
	$(eval words := $(subst /, ,$*))
	python3 ./dgs-copy.py $(word 1,$(words)) $(word 2,$(words)) $(word 3,$(words)) $(word 4,$(words))
