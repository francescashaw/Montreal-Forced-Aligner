

def data_prep(source_dir, temp_dir, dict_path, lm_path):
    """
    Prepares data for alignment from a directory of sound files with
    TextGrids (or label files)

    Parameters
    ----------
    source_dir : str
        Path to directory of sound files to align
    temp_dir : str
        Path to directory to temporary store files used in alignment
    dict_path : str
        Path to a pronunciation dictionary
    lm_path : str
        Path to a language model
    """
    pass

def transcription_prep():
    pass

def dictionary_prep():
    pass

def lm_prep():
    pass

def mfcc_prep():
    pass


def validate_dict_dir(dict_directory):
    lexiconp_path = os.path.join(dict_directory, 'lexiconp.txt')
    lexicon_path = os.path.join(dict_directory, 'lexicon.txt')
    with open(lexiconp_path, 'w', encoding = 'utf8') as outf, \
        open(lexicon_path, 'r', encoding = 'utf8') as inf:
            for line in inf:
                line = line.strip()
                word, pron = line.split('\t')
                line = '\t'.join([word, '1.0', pron])
                outf.write(line + '\n')

positions = ["_B", "_E", "_I", "_S"]

def make_position_dependent(dict_directory):
    lexiconp_path = os.path.join(dict_directory, 'lexiconp.txt')
    lexicon_temp = os.path.join(dict_directory, 'temp.txt')
    with open(lexiconp_path, 'r', encoding = 'utf8') as inf, \
        open(lexicon_temp, 'w', encoding = 'utf8') as outf:
        for line in inf:
            line = line.strip()
            w, p, phones = line.split('\t')
            phones = phones.split(' ')
            if len(phones) == 1:
                phones[0] += '_S'
            else:
                for i in range(len(phones)):
                    if i == 0:
                        phones[i] += '_B'
                    elif i == len(phones) - 1:
                        phones[i] += '_E'
                    else:
                        phones[i] += '_I'
            phones = ' '.join(phones)
            line = '\t'.join([w, p, phones])
            outf.write(line + '\n')
    os.remove(lexiconp_path)
    os.rename(lexicon_temp, lexiconp_path)

    phone_map_file = os.path.join(dict_directory, 'phone_map.txt')
    silence_file = os.path.join(dict_directory, 'silence_phones.txt')
    nonsilence_file = os.path.join(dict_directory, 'nonsilence_phones.txt')
    with open(phone_map_file, 'w', encoding = 'utf8') as outf:
        with open(silence_file, 'r', encoding = 'utf8') as inf:
            for line in inf:
                line = line.strip()
                new_phones = [line+x for x in ['', ''] + positions]
                outf.write(' '.join(new_phones) + '\n')

        with open(nonsilence_file, 'r', encoding = 'utf8') as inf:
            for line in inf:
                line = line.strip()
                new_phones = [line+x for x in [''] + positions]
                outf.write(' '.join(new_phones) + '\n')

def load_phones(path):
    phones = []
    with open(path, 'r', encoding = 'utf8') as f:
        for line in f:
            line = line.strip()
            if line == '':
                continue
            phones.append(line)
    return phones

def load_nonsilence_phones(directory):
    path = os.path.join(directory, 'nonsilence_phones.txt')
    if not os.path.exists(path):
        path = os.path.join(directory, 'nonsilence.txt')
    return load_phones(path)

def load_silence_phones(directory):
    path = os.path.join(directory, 'silence_phones.txt')
    if not os.path.exists(path):
        path = os.path.join(directory, 'silence.txt')
    return load_phones(path)

def load_disambig(directory):
    path = os.path.join(directory, 'disambig.txt')
    return load_phones(path)

def load_optional_silence(directory):
    path = os.path.join(directory, 'optional_silence.txt')
    with open(path, 'r', encoding = 'utf8') as f:
        phone = f.read().strip()
    return phone

def make_phone_sets(data_directory, shared_silence_phones):
    sharesplit = ['shared', 'split']
    if shared_silence_phones:
        sil_sharesplit = ['not-shared', 'not-split']
    else:
        sil_sharesplit = sharesplit
    dict_directory = os.path.join(data_directory, 'dict')
    lang_directory = os.path.join(data_directory, 'lang')
    phone_directory = os.path.join(lang_directory, 'phones')

    silence_phones = load_silence_phones(dict_directory)
    nonsilence_phones = load_nonsilence_phones(dict_directory)

    sets_file = os.path.join(phone_directory, 'sets.txt')
    roots_file = os.path.join(phone_directory, 'roots.txt')

    phone_silence = os.path.join(phone_directory, 'silence.txt')
    phone_nonsilence = os.path.join(phone_directory, 'nonsilence.txt')

    phone_map_file = os.path.join(dict_directory, 'phone_map.txt')
    phone_map = {}
    with open(phone_map_file, 'r', encoding = 'utf8') as inf:
        for i, line in enumerate(inf):
            line = line.strip()
            line = line.split(' ')
            phone_map[line[0]] = line[1:]


    with open(sets_file, 'w', encoding = 'utf8') as setf, \
                open(roots_file, 'w', encoding = 'utf8') as rootf:

        #process silence phones
        with open(phone_silence, 'w', encoding = 'utf8') as silf:
            for i, line in enumerate(silence_phones):
                line = line.strip()
                mapped = phone_map[line]
                setf.write(' '.join(mapped) + '\n')
                for item in mapped:
                    silf.write(item + '\n')
                if i == 0:
                    line = sil_sharesplit + mapped
                else:
                    line = sharesplit + mapped
                rootf.write(' '.join(line) + '\n')

        #process nonsilence phones
        with open(phone_nonsilence, 'w', encoding = 'utf8') as nonsilf:
            for line in nonsilence_phones:
                line = line.strip()
                mapped = phone_map[line]
                setf.write(' '.join(mapped) + '\n')
                for item in mapped:
                    nonsilf.write(item + '\n')
                line = sharesplit + mapped
                rootf.write(' '.join(line) + '\n')

    shutil.copy(os.path.join(dict_directory, 'optional_silence.txt'),
                os.path.join(phone_directory, 'optional_silence.txt'))
    shutil.copy(phone_silence, os.path.join(phone_directory, 'context_indep.txt'))
    dict_extra = os.path.join(dict_directory, 'extra_questions.txt')
    phone_extra = os.path.join(phone_directory, 'extra_questions.txt')
    with open(dict_extra, 'r', encoding = 'utf8') as inf, \
        open(phone_extra, 'w', encoding = 'utf8') as outf:
        for line in inf:
            line = line.strip()
            if line == '':
                continue
            line = line.split()
            for i in range(len(line)):
                line[i] = ' '.join(phone_map[line[i]])
            outf.write(' '.join(line) + '\n')
        for p in positions:
            line = [x + p for x in nonsilence_phones]
            outf.write(' '.join(line) + '\n')
        for p in [''] + positions:
            line = [x + p for x in silence_phones]
            outf.write(' '.join(line) + '\n')

from collections import Counter

def disambiguate_lexicon(data_directory):
    dict_directory = os.path.join(data_directory, 'dict')
    lang_directory = os.path.join(data_directory, 'lang')
    phone_directory = os.path.join(lang_directory, 'phones')
    lexiconp_path = os.path.join(dict_directory, 'lexiconp.txt')
    lexicon_disamb_path = os.path.join(dict_directory, 'lexiconp_disambig.txt')
    c = Counter()

    with open(lexiconp_path, 'r', encoding = 'utf8') as f:
        for line in f:
            line = line.strip()
            if line == '':
                continue
            line = line.split('\t')
            phones = line[-1]
            c.update([phones])
    current = {}
    with open(lexiconp_path, 'r', encoding = 'utf8') as inf, \
            open(lexicon_disamb_path, 'w', encoding = 'utf8') as outf:
        for line in inf:
            line = line.strip()
            if line == '':
                continue
            line = line.split('\t')
            phones = line[-1]
            count = c[phones]
            if count > 1:
                if phones not in current:
                    current[phones] = 0
                current[phones] += 1
                phones += ' #{}'.format(current[phones])
                line[-1] = phones
            outf.write('\t'.join(line) + '\n')

    max_disamb = max(current.values()) + 1
    with open(os.path.join(dict_directory, 'lex_ndisambig'), 'w') as f:
        f.write(str(max_disamb))

    with open(os.path.join(phone_directory, 'disambig.txt'), 'w') as f:
        for i in range(max_disamb + 1):
            f.write('#' + str(i) + '\n')

def create_phone_symbol_table(data_directory):
    dict_directory = os.path.join(data_directory, 'dict')
    lang_directory = os.path.join(data_directory, 'lang')
    phone_directory = os.path.join(lang_directory, 'phones')


    outfile = os.path.join(lang_directory, 'phones.txt')

    silence_phones = load_silence_phones(phone_directory)
    nonsilence_phones = load_nonsilence_phones(phone_directory)
    disambig = load_disambig(phone_directory)

    with open(outfile, 'w', encoding = 'utf8') as f:
        for i, p in enumerate(['eps'] + silence_phones + nonsilence_phones + disambig):
            f.write(' '.join([p, str(i)]) + '\n')

def create_word_boundaries(data_directory, position_dependent_phones):
    dict_directory = os.path.join(data_directory, 'dict')
    lang_directory = os.path.join(data_directory, 'lang')
    phone_directory = os.path.join(lang_directory, 'phones')

    silence_phones = load_silence_phones(phone_directory)
    nonsilence_phones = load_nonsilence_phones(phone_directory)

    boundary_path = os.path.join(phone_directory, 'word_boundary.txt')

    with open(boundary_path, 'w', encoding = 'utf8') as f:
        if position_dependent_phones:
            for p in silence_phones + nonsilence_phones:
                cat = 'nonword'
                if p.endswith('_B'):
                    cat = 'begin'
                elif p.endswith('_S'):
                    cat = 'singleton'
                elif p.endswith('_I'):
                    cat = 'internal'
                elif p.endswith('_E'):
                    cat = 'end'
                f.write(' '.join([p, cat])+'\n')

def create_word_file(data_directory):
    dict_directory = os.path.join(data_directory, 'dict')
    lang_directory = os.path.join(data_directory, 'lang')
    phone_directory = os.path.join(lang_directory, 'phones')
    lexiconp_path = os.path.join(dict_directory, 'lexiconp.txt')
    words_path = os.path.join(lang_directory, 'words.txt')
    words = set()

    with open(lexiconp_path, 'r', encoding = 'utf8') as f:
        for line in f:
            line = line.strip()
            if line == '':
                continue
            line = line.split('\t')
            words.add(line[0])

    with open(words_path, 'w', encoding = 'utf8') as f:
        i = 0
        f.write('{} {}\n'.format('<eps>', i))
        for w in sorted(words):
            i += 1
            f.write('{} {}\n'.format(w, i))

        f.write('{} {}\n'.format('#0', i + 1))
        f.write('{} {}\n'.format('<s>', i + 2))
        f.write('{} {}\n'.format('<\s>', i + 3))

def load_phone_to_int(lang_directory):
    path = os.path.join(lang_directory, 'phones.txt')
    mapping = {}
    with open(path, 'r', encoding = 'utf8') as f:
        for line in f:
            line = line.strip()
            if line == '':
                continue
            symbol, i = line.split(' ')
            mapping[symbol] = i
    return mapping

def load_word_to_int(lang_directory):
    path = os.path.join(lang_directory, 'words.txt')
    mapping = {}
    with open(path, 'r', encoding = 'utf8') as f:
        for line in f:
            line = line.strip()
            if line == '':
                continue
            symbol, i = line.split(' ')
            mapping[symbol] = i
    return mapping

def prepare_align_dict(data_directory):
    dict_directory = os.path.join(data_directory, 'dict')
    lang_directory = os.path.join(data_directory, 'lang')
    phone_directory = os.path.join(lang_directory, 'phones')

    lexiconp_path = os.path.join(dict_directory, 'lexiconp.txt')
    lexicon_ali_path = os.path.join(phone_directory, 'align_lexicon.txt')
    lexicon_ali_int_path = os.path.join(phone_directory, 'align_lexicon.int')

    opt_sil = load_optional_silence(dict_directory)

    words = set(['<eps> {}'.format(opt_sil)])

    with open(lexiconp_path, 'r', encoding = 'utf8') as f:
        for line in f:
            line = line.strip()
            if line == '':
                continue
            w, p, phones = line.split('\t')
            words.add('{} {}'.format(w, phones))

    phone_mapping = load_phone_to_int(lang_directory)
    word_mapping = load_word_to_int(lang_directory)
    with open(lexicon_ali_path, 'w', encoding = 'utf8') as f, \
        open(lexicon_ali_int_path, 'w', encoding = 'utf8') as f2:
        for w in sorted(words):
            f.write('{}\n'.format(w))
            symbols = w.split(' ')
            word_int = word_mapping[symbols[0]]
            phone_ints = [phone_mapping[x] for x in symbols[1:]]
            phones = ' '.join(phone_ints)
            f2.write('{} {} {}\n'.format(word_int, word_int, phones))

import math
import subprocess

def make_lexicon_fst(data_directory, pronunciation_probabilities = True,
                    sil_prob = 0.5):
    dict_directory = os.path.join(data_directory, 'dict')
    lang_directory = os.path.join(data_directory, 'lang')
    phone_directory = os.path.join(lang_directory, 'phones')

    silphone = load_optional_silence(phone_directory)
    phone_mapping = load_phone_to_int(lang_directory)
    word_mapping = load_word_to_int(lang_directory)

    lexicon_disamb_path = os.path.join(dict_directory, 'lexiconp_disambig.txt')

    loopstate = 0
    nextstate = 1
    lexicon_fst_path = os.path.join(lang_directory, 'lexicon.text.fst')
    with open(lexicon_disamb_path, 'r', encoding = 'utf8') as f, \
        open(lexicon_fst_path, 'w', encoding = 'utf8') as outf:
        for line in f:
            line = line.strip()
            if line == '':
                continue
            elements = line.split('\t')

            w = elements.pop(0)
            if not pronunciation_probabilities:
                pron_cost = 0
            else:
                pron_prob = elements.pop(0)
                pron_cost = -1 * math.log(float(pron_prob))

            pron_cost_string = ''
            if pron_cost != 0:
                pron_cost_string = '\t{}'.pron_cost

            s = loopstate
            word_or_eps = w
            elements = elements[-1].split(' ')
            while len(elements) > 0:
                p = elements.pop(0)
                if len(elements) > 0:
                    ns = nextstate
                    nextstate += 1
                else:
                    ns = loopstate
                outf.write('\t'.join(map(str,[s, ns, p, word_or_eps])) + pron_cost_string + '\n')
                word_or_eps = '<eps>'
                pron_cost_string = ""
                s = ns
        outf.write("{}\t{}\n".format(loopstate, 0))
    temp_fst_path = os.path.join(lang_directory, 'temp.fst')
    phones_file_path = os.path.join(lang_directory, 'phones.txt')
    words_file_path = os.path.join(lang_directory, 'words.txt')
    subprocess.call(['fstcompile', '--isymbols={}'.format(phones_file_path),
                    '--osymbols={}'.format(words_file_path),
                    '--keep_isymbols=false','--keep_osymbols=false',
                    lexicon_fst_path, temp_fst_path])
    phone_disambig_symbol = phone_mapping['#0']
    phone_disambig_symbol_path = os.path.join(phone_directory, 'phone_disambig_symbol')
    with open(phone_disambig_symbol_path, 'w') as f:
        f.write(str(phone_disambig_symbol))
    word_disambig_symbol = word_mapping['#0']
    word_disambig_symbol_path = os.path.join(phone_directory, 'word_disambig_symbol')
    with open(word_disambig_symbol_path, 'w') as f:
        f.write(str(word_disambig_symbol))

    subprocess.call(['fstaddselfloops',
        phone_disambig_symbol_path, word_disambig_symbol_path,
        temp_fst_path, temp_fst_path])

    output_fst = os.path.join(lang_directory, 'L_disambig.fst')
    subprocess.call(['fstarcsort', '--sort_type=olabel',
                temp_fst_path, output_fst])

def prepare_lang(data_directory, oov_code = "<unk>",
                position_dependent_phones = True,
                num_sil_states = 5,
                num_nonsil_states = 3,
                share_silence_phones = False,
                sil_prob = 0.5,
                reverse = False):
    dict_directory = os.path.join(data_directory, 'dict')
    lang_directory = os.path.join(data_directory, 'lang')
    phone_dir = os.path.join(lang_directory, 'phones')
    validate_dict_dir(dict_directory)

    if position_dependent_phones:
        make_position_dependent(dict_directory)

    os.makedirs(phone_dir, exist_ok = True)
    make_phone_sets(data_directory, share_silence_phones)
    disambiguate_lexicon(data_directory)
    create_phone_symbol_table(data_directory)
    create_word_boundaries(data_directory, position_dependent_phones)
    create_word_file(data_directory)
    prepare_align_dict(data_directory)
    make_lexicon_fst(data_directory)