#!/usr/bin/env python
# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai

# Changelog
#  0.11 - Version by adamselene
#  0.11pd - Tweaked version by pdurrant
#  0.12 - extracts pictures too, and all into a folder.
#  0.13 - added back in optional output dir for those who don't want it based on infile
#  0.14 - auto flush stdout and wrapped in main, added proper return codes
#  0.15 - added support for metadata
#  0.16 - metadata now starting to be output as an opf file (PD)
#  0.17 - Also created tweaked text as source for Mobipocket Creator
#  0.18 - removed raw mobi file completely but kept _meta.html file for ease of conversion
#  0.19 - added in metadata for ASIN, Updated Title and Rights to the opf
#  0.20 - remove _meta.html since no longer needed
#  0.21 - Fixed some typos in the opf output, and also updated handling
#         of test for trailing data/multibyte characters
#  0.22 - Fixed problem with > 9 images
#  0.23 - Now output Start guide item
#  0.24 - Set firstaddl value for 'TEXtREAd'
#  0.25 - Now added character set metadata to html file for utf-8 files.
#  0.26 - Dictionary support added. Image handling speed improved.
#         For huge files create temp files to speed up decoding.
#         Language decoding fixed. Metadata is now converted to utf-8 when written to opf file.
#  0.27 - Add idx:entry attribute "scriptable" if dictionary contains entry length tags.
#         Don't save non-image sections as images. Extract and save source zip file
#         included by kindlegen as kindlegensrc.zip.
#  0.28 - Added back correct image file name extensions, created FastConcat class to simplify and clean up
#  0.29 - Metadata handling reworked, multiple entries of the same type are now supported.
#         Several missing types added.
#         FastConcat class has been removed as in-memory handling with lists is faster, even for huge files.
#  0.30 - Add support for outputting **all** metadata values - encode content with hex if of unknown type
#  0.31 - Now supports Print Replica ebooks, outputting PDF and mysterious data sections
#  0.32 - Now supports NCX file extraction/building.
#                 Overhauled the structure of mobiunpack to be more class oriented.
#  0.33 - Split Classes ito separate files and added prelim support for KF8 format eBooks
#  0.34 - Improved KF8 support, guide support, bug fixes
#  0.35 - Added splitting combo mobi7/mobi8 into standalone mobi7 and mobi8 files
#         Also handle mobi8-only file properly
#  0.36 - very minor changes to support KF8 mobis with no flow items, no ncx, etc
#  0.37 - separate output, add command line switches to control, interface to Mobi_Unpack.pyw
#  0.38 - improve split function by resetting flags properly, fix bug in Thumbnail Images
#  0.39 - improve split function so that ToC info is not lost for standalone mobi8s
#  0.40 - make mobi7 split match official versions, add support for graphic novel metadata,
#         improve debug for KF8
#  0.41 - fix when StartOffset set to 0xffffffff, fix to work with older mobi versions,
#         fix other minor metadata issues
#  0.42 - add new class interface to allow it to integrate more easily with internal calibre routines
#  0.43 - bug fixes for new class interface
#  0.44 - more bug fixes and fix for potnetial bug caused by not properly closing created zip archive
#  0.45 - sync to version in the new Mobi_Unpack plugin
#  0.46 - fixes for: obfuscated fonts, improper toc links and ncx, add support for opentype fonts
#  0.47 - minor opf improvements
#  0.48 - ncx link fixes
#  0.49 - use azw3 when splitting mobis
#  0.50 - unknown change
#  0.51 - fix for converting filepos links to hrefs, Added GPL3 notice, made KF8 extension just '.azw3'
#  0.52 - fix for cover metadata (no support for Mobipocket Creator)
#  0.53 - fix for proper identification of embedded fonts, added new metadata items
#  0.54 - Added error-handling so wonky embedded fonts don't bomb the whole unpack process,
#         entity escape KF8 metadata to ensure valid OPF.
#  0.55  Strip extra StartOffset EXTH from the mobi8 header when splitting, keeping only the relevant one
#         For mobi8 files, don't generate duplicate guide entries from the metadata if we could extract one
#         from the OTH table.
#  0.56 - Added further entity escaping of OPF text.
#         Allow unicode string file paths to be passed as arguments to the unpackBook method without blowing up later
#         when the attempt to "re"-unicode a portion of that filename occurs in the process_all_mobi_headers method.
#  0.57 - Fixed eror when splitting Preview files downloaded from KDP website
#  0.58 - Output original kindlegen build log ('CMET' record) if included in the package.
#  0.58 - Include and extend functionality of DumpMobiHeader, replacing DEBUG with DUMP
#  0.59 - Much added DUMP functionality, including full dumping and descriptions of sections
#  0.60 - Bug fixes in opf, div tables, bad links, page breaks, section descriptions
#       - plus a number of other bug fixed that were found by Sergey Dubinets
#       - fixs for file/paths that require full unicode to work properly
#       - replace subprocess with multiprocessing to remove need for unbuffered stdout
#  0.61 - renamed to be KindleUnpack and more unicode/utf-8 path bug fixes and other minor fixes
#  0.62 - fix for multiprocessing on Windows, split fixes, opf improvements
#  0.63 - Modified to process right to left page progression books properly.
#       - Added some id_map_strings and RESC section processing; metadata and
#       - spine in the RESC are integrated partly to content.opf.
#  0.63a- Separated K8 RESC processor to an individual file. Bug fixes. Added cover page creation.
#  0.64 - minor bug fixes to more properly handle unicode command lines, and support for more jpeg types
#  0.64a- Modifed to handle something irregular mobi and azw3 files.
#  0.64b- Modifed to create k8resc.spine for no RECS files.
#  0.65 - Bug fixes to shorten title and remove epub3 "properties" to make the output epub2 compliant
#  0.65a- Bug fixes to extract RESC section correctly, to prevent item id confliction
#       - and to process multiline comments in RESC.
#  0.66 - Bug fix to deal with missing first resource information sometimes generated by calibre
#  0.66a- Fixed minor bugs, which probably do not affect the output anything
#  0.67 - Fixed Mobi Split functionality bug with azw3 images not being properly copied
#  0.68 - preliminary support for handling PAGE sections to create page-map.xml
#  0.69 - preliminary support for CONT and CRES for HD Images
#  0.70 - preliminary support for decoding apnx files when used with azw3 ebooks
#  0.71 - extensive refactoring of kindleunpack.py to make it more manageable

DUMP = False
""" Set to True to dump all possible information. """

WRITE_RAW_DATA = False
""" Set to True to create additional files with raw data for debugging/reverse engineering. """

SPLIT_COMBO_MOBIS = False
""" Set to True to split combination mobis into mobi7 and mobi8 pieces. """

PROC_K8RESC = True
""" Process K8 RESC section. """

CREATE_COVER_PAGE = True # XXX experimental
""" Create and insert a cover xhtml page. """

EOF_RECORD = chr(0xe9) + chr(0x8e) + "\r\n"
""" The EOF record content. """

TERMINATION_INDICATOR1 = chr(0x0)
TERMINATION_INDICATOR2 = chr(0x0) + chr(0x0)
TERMINATION_INDICATOR3 = chr(0x0) + chr(0x0) + chr(0x0)

KINDLEGENSRC_FILENAME = "kindlegensrc.zip"
""" The name for the kindlegen source archive. """

KINDLEGENLOG_FILENAME = "kindlegenbuild.log"
""" The name for the kindlegen build log. """

K8_BOUNDARY = "BOUNDARY"
""" The section data that divides K8 mobi ebooks. """


import sys
import os

import locale
import codecs

from utf8_utils import utf8_argv, add_cp65001_codec, utf8_str
add_cp65001_codec()
from path import pathof


import array, struct, re, imghdr, zlib, zipfile, datetime
import getopt, binascii

class unpackException(Exception):
    pass


# import the kindleunpack support libraries
from unpack_structure import fileNames
from mobi_sectioner import Sectionizer, describe
from mobi_header import MobiHeader, dump_contexth
from mobi_utils import getLanguage, toHex, fromBase32, toBase32, mangle_fonts
from mobi_opf import OPFProcessor
from mobi_html import HTMLProcessor, XHTMLK8Processor
from mobi_ncx import ncxExtract
from mobi_k8proc import K8Processor
from mobi_split import mobi_split
from mobi_k8resc import K8RESCProcessor, CoverProcessor
from mobi_pagemap import PageMapProcessor
from mobi_dict import dictSupport


def renameCoverImage(metadata, files, imgnames):
    global CREATE_COVER_PAGE
    if CREATE_COVER_PAGE:
        if 'CoverOffset' in metadata.keys():
            i = int(metadata['CoverOffset'][0])
            if imgnames[i] != None:
                old_name = imgnames[i]
                if not 'cover' in old_name:
                    new_name = re.sub(r'image', 'cover', old_name)
                    imgnames[i] = new_name
                    oldimg = os.path.join(files.imgdir, old_name)
                    newimg = os.path.join(files.imgdir, new_name)
                    if os.path.exists(pathof(oldimg)):
                        if os.path.exists(pathof(newimg)):
                            os.remove(pathof(newimg))
                        os.rename(pathof(oldimg), pathof(newimg))
    return imgnames


def processSRCS(i, files, imgnames, sect, data):
    # extract the source zip archive and save it.
    print "File contains kindlegen source archive, extracting as %s" % KINDLEGENSRC_FILENAME
    srcname = os.path.join(files.outdir, KINDLEGENSRC_FILENAME)
    open(pathof(srcname), 'wb').write(data[16:])
    imgnames.append(None)
    sect.setsectiondescription(i,"Zipped Source Files")
    return imgnames


def processPAGE(i, files, imgnames, sect, data, pagemapproc):
    # process the page map information so it can be further processed later
    pagemapproc = PageMapProcessor(mh, data)
    imgnames.append(None)
    sect.setsectiondescription(i,"PageMap")
    return imagenames, pagemapproc


def processCMET(i, files, imgnames, sect, data):
    # extract the build log
    print "File contains kindlegen build log, extracting as %s" % KINDLEGENLOG_FILENAME
    srcname = os.path.join(files.outdir, KINDLEGENLOG_FILENAME)
    open(pathof(srcname), 'wb').write(data[10:])
    imgnames.append(None)
    sect.setsectiondescription(i,"Kindlegen log")
    return imgnames


# fonts only exist in KF8 ebooks
# Format:  bytes  0 -  3:  'FONT'    
#          bytes  4 -  7:  uncompressed size
#          bytes  8 - 11:  flags
#              flag bit 0x0001 - zlib compression
#              flag bit 0x0002 - obfuscated with xor string
#          bytes 12 - 15:  offset to start of compressed font data
#          bytes 16 - 19:  length of xor string stored before the start of the comnpress font data
#          bytes 20 - 23:  start of xor string
def processFONT(i, files, imgnames, sect, data, obfuscate_data):
    fontname = "font%05d" % i
    ext = '.dat'
    font_error = False
    font_data = data 
    try:
        usize, fflags, dstart, xor_len, xor_start = struct.unpack_from('>LLLLL',data,4)
    except:
        print "Failed to extract font: {0:s} from section {1:d}".format(fontname,i)
        font_error = True
        ext = '.failed'
        pass
    if not font_error:
        print "Extracting font:", fontname
        font_data = data[dstart:]
        extent = len(font_data)
        extent = min(extent, 1040)
        if fflags & 0x0002:
            # obfuscated so need to de-obfuscate the first 1040 bytes
            key = bytearray(data[xor_start: xor_start+ xor_len])
            buf = bytearray(font_data)
            for n in xrange(extent):
                buf[n] ^=  key[n%xor_len]
            font_data = bytes(buf)
        if fflags & 0x0001:
            # ZLIB compressed data
            font_data = zlib.decompress(font_data)
        hdr = font_data[0:4]
        if hdr == '\0\1\0\0' or hdr == 'true' or hdr == 'ttcf':
            ext = '.ttf'
        elif hdr == 'OTTO':
            ext = '.otf'
        else:
            print "Warning: unknown font header %s" % hdr.encode('hex')
        if (ext == '.ttf' or ext == '.otf') and (fflags & 0x0002):
            obfuscate_data.append(fontname + ext)
        fontname += ext
        outfnt = os.path.join(files.imgdir, fontname)
        open(pathof(outfnt), 'wb').write(font_data)
        imgnames.append(fontname)
        sect.setsectiondescription(i,"Font {0:s}".format(fontname))
    return imgnames, obfuscate_data


def processCRES(i, files, imgnames, sect, data):
    # extract an HDImage
    global DUMP
    data = data[12:]
    imgtype = imghdr.what(None, data)

    # imghdr only checks for JFIF or Exif JPEG files. Apparently, there are some
    # with only the magic JPEG bytes out there...
    # ImageMagick handles those, so, do it too.
    if imgtype is None and data[0:2] == b'\xFF\xD8':
        # Get last non-null bytes
        last = len(data)
        while (data[last-1:last] == b'\x00'):
            last-=1
        # Be extra safe, check the trailing bytes, too.
        if data[last-2:last] == b'\xFF\xD9':
            imgtype = "jpeg"

    if imgtype is None:
        print "Warning: Section %s does not contain a recognised resource" % i
        imgnames.append(None)
        sect.setsectiondescription(i,"Mysterious CRES data, first four bytes %s" % describe(data[0:4]))
        if DUMP:
            fname = "unknown%05d.dat" % i
            outname= os.path.join(files.outdir, fname)
            open(pathof(outname), 'wb').write(data)
            sect.setsectiondescription(i,"Mysterious CRES data, first four bytes %s extracting as %s" % (describe(data[0:4]), fname))
    else:
        imgname = "HDimage%05d.%s" % (i, imgtype)
        print "Extracting HD image: {0:s} from section {1:d}".format(imgname,i)
        outimg = os.path.join(files.hdimgdir, imgname)
        open(pathof(outimg), 'wb').write(data)
        imgnames.append(None)
        sect.setsectiondescription(i,"Optional HD Image {0:s}".format(imgname))

    return imgnames


def processCONT(i, files, imgnames, sect, data):
    global DUMP
    # process a container header, most of this is unknown
    # right now only extract its EXTH
    dt = data[0:12]
    if dt == "CONTBOUNDARY":
        imgnames.append(None)
        sect.setsectiondescription(i,"CONTAINER BOUNDARY")
        return
    sect.setsectiondescription(i,"CONT Header")
    if DUMP:
        cpage, = struct.unpack_from('>L', data, 12)
        contexth = data[48:]
        print "\n\nContainer EXTH Dump"
        dump_contexth(cpage, contexth)
    imgnames.append(None)
    return imgnames


def processkind(i, files, imgnames, sect, data):
    global DUMP
    dt = data[0:12]
    if dt == "kindle:embed":
        if DUMP:
            print "\n\nHD Image Container Description String"
            print data
        sect.setsectiondescription(i,"HD Image Container Description String")
        imgnames.append(None)
    return imgnames


def processRESC(i, files, imgnames, sect, data, resc):
    global DUMP
    # spine information from the original content.opf
    unknown1, unknown2, unknown3 = struct.unpack_from('>LLL',data,4)
    data_ = data[16:]
    m_header = re.match(r'^\w+=(\w+)\&\w+=(\d+)&\w+=(\d+)', data_)
    resc_header = m_header.group()
    resc_size = fromBase32(m_header.group(1))
    resc_version = int(m_header.group(2))
    resc_type = int(m_header.group(3))

    resc_rawbytes = len(data_) - m_header.end()
    if resc_rawbytes == resc_size:
        # Most RESC has a nul string at its tail but some does not.
        resc_length = resc_size
    else:
        end_pos = data_.find('\x00', m_header.end())
        if end_pos < 0:
            resc_length = resc_rawbytes
        else:
            resc_length = end_pos - m_header.end()
        if resc_length != resc_size:
            if resc_rawbytes > resc_size:
                print "Warning: the RESC section length({:d}bytes) does not match to indicated size({:d}bytes).".format(resc_length, resc_size)
            else:
                print "Warning: the RESC section might be broken. Its length({:d}bytes) is shorter than indicated size({:d}bytes).".format(resc_length, resc_size)
    resc_data = data_[m_header.end():m_header.end()+resc_length]
    resc = [resc_version, resc_type, resc_data]

    if DUMP:
        rescname = "RESC%05d.dat" % i
        print "Extracting Resource: ", rescname
        outrsc = os.path.join(files.outdir, rescname)
        f = open(pathof(outrsc), 'w')
        f.write('section size = {0:d} bytes, size in header = {1:d} bytes, valid length = {2:d} bytes\n'.format(resc_rawbytes, resc_size, resc_length))
        f.write('unknown(hex) = {:08X}\n'.format(unknown1))
        f.write('unknown(hex) = {:08X}\n'.format(unknown2))
        f.write('unknown(hex) = {:08X}\n'.format(unknown3))
        f.write(resc_header + '\n')
        f.write(resc_data)
        #f.write(data_[m_header.end():])
        f.close()

    imgnames.append(None)
    sect.setsectiondescription(i,"K8 RESC section")
    return imgnames, resc


def processImage(i, files, imgnames, sect, data):
    global DUMP
    # Extract an Image

    # Get the proper file extension
    imgtype = imghdr.what(None, data)

    # imghdr only checks for JFIF or Exif JPEG files. Apparently, there are some
    # with only the magic JPEG bytes out there...
    # ImageMagick handles those, so, do it too.
    if imgtype is None and data[0:2] == b'\xFF\xD8':
        # Get last non-null bytes
        last = len(data)
        while (data[last-1:last] == b'\x00'):
            last-=1
        # Be extra safe, check the trailing bytes, too.
        if data[last-2:last] == b'\xFF\xD9':
            imgtype = "jpeg"

    if imgtype is None:
        print "Warning: Section %s does not contain a recognised resource" % i
        imgnames.append(None)
        sect.setsectiondescription(i,"Mysterious Section, first four bytes %s" % describe(data[0:4]))
        if DUMP:
            fname = "unknown%05d.dat" % i
            outname= os.path.join(files.outdir, fname)
            open(pathof(outname), 'wb').write(data)
            sect.setsectiondescription(i,"Mysterious Section, first four bytes %s extracting as %s" % (describe(data[0:4]), fname))
    else:
        imgname = "image%05d.%s" % (i, imgtype)
        print "Extracting image: {0:s} from section {1:d}".format(imgname,i)
        outimg = os.path.join(files.imgdir, imgname)
        open(pathof(outimg), 'wb').write(data)
        imgnames.append(imgname)
        sect.setsectiondescription(i,"Image {0:s}".format(imgname))
    return imgnames


def processPrintReplica(metadata, files, imgnames, mh):
    global DUMP
    global WRITE_RAW_DATA
    rawML = mh.getRawML()
    if DUMP or WRITE_RAW_DATA:
        outraw = os.path.join(files.outdir,files.getInputFileBasename() + '.rawpr')
        open(pathof(outraw),'wb').write(rawML)

    filenames = []
    print "Print Replica ebook detected"
    try:
        numTables, = struct.unpack_from('>L', rawML, 0x04)
        tableIndexOffset = 8 + 4*numTables
        # for each table, read in count of sections, assume first section is a PDF
        # and output other sections as binary files
        paths = []
        for i in xrange(numTables):
            sectionCount, = struct.unpack_from('>L', rawML, 0x08 + 4*i)
            for j in xrange(sectionCount):
                sectionOffset, sectionLength, = struct.unpack_from('>LL', rawML, tableIndexOffset)
                tableIndexOffset += 8
                if j == 0:
                    entryName = os.path.join(files.outdir, files.getInputFileBasename() + ('.%03d.pdf' % (i+1)))
                else:
                    entryName = os.path.join(files.outdir, files.getInputFileBasename() + ('.%03d.%03d.data' % ((i+1),j)))
                open(pathof(entryName), 'wb').write(rawML[sectionOffset:(sectionOffset+sectionLength)])
    except Exception, e:
        print 'Error processing Print Replica: ' + str(e)

    filenames.append(['', files.getInputFileBasename() + '.pdf'])
    usedmap = {}
    for name in imgnames:
        if name != None:
            usedmap[name] = 'used'
    opf = OPFProcessor(files, metadata, filenames, imgnames, False, mh, usedmap)
    opf.writeOPF()



def processMobi8(mh, metadata, sect, files, imgnames, pagemapproc, resc, obfuscate_data, apnxfile=None):
    global DUMP
    global WRITE_RAW_DATA

    # extract raw markup langauge
    rawML = mh.getRawML()
    if DUMP or WRITE_RAW_DATA:
        outraw = os.path.join(files.k8dir,files.getInputFileBasename() + '.rawml')
        open(pathof(outraw),'wb').write(rawML)

    # KF8 require other indexes which contain parsing information and the FDST info
    # to process the rawml back into the xhtml files, css files, svg image files, etc
    k8proc = K8Processor(mh, sect, files, DUMP)
    k8proc.buildParts(rawML)

    # collect information for the guide first
    guidetext = k8proc.getGuideText()

    # if the guide was empty, add in any guide info from metadata, such as StartOffset
    if not guidetext and 'StartOffset' in metadata.keys():
        # Apparently, KG 2.5 carries over the StartOffset from the mobi7 part...
        # Taking that into account, we only care about the *last* StartOffset, which
        # should always be the correct one in these cases (the one actually pointing
        # to the right place in the mobi8 part).
        starts = metadata['StartOffset']
        last_start = starts[-1]
        last_start = int(last_start)
        if last_start == 0xffffffff:
            last_start = 0
        seq, idtext = k8proc.getDivTblInfo(last_start)
        filename, idtext = k8proc.getIDTagByPosFid(toBase32(seq), '0000000000')
        linktgt = filename
        if idtext != '':
            linktgt += '#' + idtext
        guidetext += '<reference type="text" href="Text/%s" />\n' % linktgt

    # if apnxfile is passed in use if for page map information 
    if apnxfile != None and pagemapproc == None:
        apnxdata = "00000000" + file(apnxfile, 'rb').read()
        pagemapproc = PageMapProcessor(mh, apnxdata)

    # generate the page map
    pagemapxml = ''
    if pagemapproc != None:
        pagemapxml = pagemapproc.generateKF8PageMapXML(k8proc)
        outpm = os.path.join(files.k8oebps,'page-map.xml')
        open(pathof(outpm),'wb').write(pagemapxml)
        if DUMP:
            print pagemapproc.getNames()
            print pagemapproc.getOffsets()
            print "\n\nPage Map"
            print pagemapxml

    # process the toc ncx
    # ncx map keys: name, pos, len, noffs, text, hlvl, kind, pos_fid, parent, child1, childn, num
    print "Processing ncx / toc"
    ncx = ncxExtract(mh, files)
    ncx_data = ncx.parseNCX()
    # extend the ncx data with filenames and proper internal idtags
    for i in range(len(ncx_data)):
        ncxmap = ncx_data[i]
        [junk1, junk2, junk3, fid, junk4, off] = ncxmap['pos_fid'].split(':')
        filename, idtag = k8proc.getIDTagByPosFid(fid, off)
        ncxmap['filename'] = filename
        ncxmap['idtag'] = idtag
        ncx_data[i] = ncxmap
    ncx.writeK8NCX(ncx_data, metadata)

    # convert the rawML to a set of xhtml files
    print "Building an epub-like structure"
    htmlproc = XHTMLK8Processor(imgnames, k8proc)
    usedmap = htmlproc.buildXHTML()

    # write out the xhtml svg, and css files
    filenames = []
    n =  k8proc.getNumberOfParts()
    for i in range(n):
        part = k8proc.getPart(i)
        [skelnum, dir, filename, beg, end, aidtext] = k8proc.getPartInfo(i)
        filenames.append([dir, filename])
        fname = os.path.join(files.k8oebps,dir,filename)
        open(pathof(fname),'wb').write(part)
    n = k8proc.getNumberOfFlows()
    for i in range(1, n):
        [type, format, dir, filename] = k8proc.getFlowInfo(i)
        flowpart = k8proc.getFlow(i)
        if format == 'file':
            filenames.append([dir, filename])
            fname = os.path.join(files.k8oebps,dir,filename)
            open(pathof(fname),'wb').write(flowpart)

    k8resc = None

    # ****FIXME****:  pass k8proc into mobi_k8resc routines and offload most of the work done here to mobi_k8resc
    # process RESC spine information

    if PROC_K8RESC:
        # Retrieve a spine (and a metadata) from RESC section.
        # Get correspondences between itemes in a spine in RECS and ones in a skelton.
        k8resc = K8RESCProcessor(resc)
        n =  k8proc.getNumberOfParts()
        if k8resc.spine == None: # make a spine if not able to retrieve from a RESC section.
            spine = [['<spine toc="ncx">', None, None, True, None]]
            for i in range(n):
                spine.append(['<itemref/>', i, 'skel{:d}'.format(i), False, None])
            spine.append(['</spine>', None, None, True, None])
            k8resc.spine = spine
            k8resc.createSkelidToSpineIndexDict()
        for i in range(n):
            # Import skelnum and filename to K8RescProcessor.
            [skelnum, dir, filename, beg, end, aidtext] = k8proc.getPartInfo(i)
            index = k8resc.getSpineIndexBySkelid(skelnum)
            k8resc.setFilenameToSpine(index, filename)

        if CREATE_COVER_PAGE:
            cover = CoverProcessor(files, metadata, imgnames)
            # Create a cover page if first spine item has no correspondence.
            createCoverPage = False
            index = k8resc.getSpineStartIndex()
            if k8resc.getSpineSkelid(index) < 0:
                createCoverPage = True
            else:
                filename = k8resc.getFilenameFromSpine(index)
                if filename != None:
                    fname = os.path.join(files.k8oebps, dir, filename)
                    f = open(pathof(fname), 'r')
                    if f != None:
                        xhtml = f.read()
                        f.close()
                        cover_img = cover.getImageName()
                        if cover_img != None and not cover_img in xhtml:
                            k8resc.insertSpine(index, 'inserted_cover', -1, None)
                            k8resc.createSkelidToSpineIndexDict()
                            createCoverPage = True
            if createCoverPage:
                cover.writeXHTML()
                filename = cover.getXHTMLName()
                dir = os.path.relpath(files.k8text, files.k8oebps)
                filenames.append([dir, filename])
                k8resc.setFilenameToSpine(index, filename)
                k8resc.setSpineAttribute(index, 'linear', 'no')
                guidetext += cover.guide_toxml()

        k8resc.createFilenameToSpineIndexDict()

    # create the opf
    opf = OPFProcessor(files, metadata, filenames, imgnames, ncx.isNCX, mh, usedmap, pagemapxml, guidetext, k8resc)
    if obfuscate_data:
        uuid = opf.writeOPF(True)
    else:
        uuid = opf.writeOPF()

    # make an epub-like structure of it all
    files.makeEPUB(usedmap, obfuscate_data, uuid)


def processMobi7(mh, metadata, sect, files, imgnames):
    global DUMP
    global WRITE_RAW_DATA
    # An original Mobi
    rawML = mh.getRawML()
    if DUMP or WRITE_RAW_DATA:
        outraw = os.path.join(files.mobi7dir,files.getInputFileBasename() + '.rawml')
        open(pathof(outraw),'wb').write(rawML)

    # process the toc ncx
    # ncx map keys: name, pos, len, noffs, text, hlvl, kind, pos_fid, parent, child1, childn, num
    ncx = ncxExtract(mh, files)
    ncx_data = ncx.parseNCX()
    ncx.writeNCX(metadata)

    positionMap = {}

    # if Dictionary build up the positionMap
    if mh.isDictionary():
        if mh.DictInLanguage():
            metadata['DictInLanguage'] = mh.DictInLanguage()
        if mh.DictOutLanguage():
            metadata['DictOutLanguage'] = mh.DictOutLanguage()
        positionMap = dictSupport(mh, sect).getPositionMap()

    # convert the rawml back to Mobi ml
    proc = HTMLProcessor(files, metadata, imgnames)
    srctext = proc.findAnchors(rawML, ncx_data, positionMap)
    srctext, usedmap = proc.insertHREFS()

    # write the proper mobi html
    filenames=[]
    fname = files.getInputFileBasename() + '.html'
    filenames.append(['', fname])
    outhtml = os.path.join(files.mobi7dir, fname)
    open(pathof(outhtml), 'wb').write(srctext)

    # extract guidetext from srctext
    guidetext =''
    pagemapxml = ''
    guidematch = re.search(r'''<guide>(.*)</guide>''',srctext,re.IGNORECASE+re.DOTALL)
    if guidematch:
        replacetext = r'''href="'''+filenames[0][1]+r'''#filepos\1"'''
        guidetext = re.sub(r'''filepos=['"]{0,1}0*(\d+)['"]{0,1}''', replacetext, guidematch.group(1))
        guidetext += '\n'
        if isinstance(guidetext, unicode):
            guidetext = guidetext.decode(mh.codec).encode("utf-8")
        else:
            guidetext = unicode(guidetext, mh.codec).encode("utf-8")

    # create an OPF
    opf = OPFProcessor(files, metadata, filenames, imgnames, ncx.isNCX, mh, usedmap, pagemapxml, guidetext)
    opf.writeOPF()


def processUnknownSections(mh, sect, files, K8Boundary):
    global DUMP
    global TERMINATION_INDICATOR1
    global TERMINATION_INDICATOR2
    global TERMINATION_INDICATOR3
    if DUMP:
        print "Unpacking any remaining unknown records"
    beg = mh.start
    end = sect.num_sections
    if beg < K8Boundary:
        # then we're processing the first part of a combination file
        end = K8Boundary
    for i in xrange(beg, end):
        if sect.sectiondescriptions[i] == "":
            data = sect.loadSection(i)
            type = data[0:4]
            if  type == TERMINATION_INDICATOR3:
                description = "Termination Marker 3 Nulls"
            elif type == TERMINATION_INDICATOR2:
                description = "Termination Marker 2 Nulls"
            elif type == TERMINATION_INDICATOR1:
                description = "Termination Marker 1 Null"
            elif type == "INDX":
                fname = "Unknown%05d_INDX.dat" % i
                description = "Unknown INDX section"
                if DUMP:
                    outname= os.path.join(files.outdir, fname)
                    open(pathof(outname), 'wb').write(data)
                    print "Extracting %s: %s from section %d" % (description, fname, i)
                    description = description + ", extracting as %s" % fname
            else:
                fname = "unknown%05d.dat" % i
                description = "Mysterious Section, first four bytes %s" % describe(data[0:4])
                if DUMP:
                    outname= os.path.join(files.outdir, fname)
                    open(pathof(outname), 'wb').write(data)
                    print "Extracting %s: %s from section %d" % (description, fname, i)
                    description = description + ", extracting as %s" % fname
            sect.setsectiondescription(i, description)


def process_all_mobi_headers(files, apnxfile, sect, mhlst, K8Boundary, k8only=False):
    global DUMP
    global WRITE_RAW_DATA
    imgnames = []
    resc = None
    for mh in mhlst:
        pagemapproc = None
        if mh.isK8():
            sect.setsectiondescription(mh.start,"KF8 Header")
            mhname = os.path.join(files.outdir,"header_K8.dat")
            print "Processing K8 section of book..."
        elif mh.isPrintReplica():
            sect.setsectiondescription(mh.start,"Print Replica Header")
            mhname = os.path.join(files.outdir,"header_PR.dat")
            print "Processing PrintReplica section of book..."
        else:
            if mh.version == 0:
                sect.setsectiondescription(mh.start, "PalmDoc Header".format(mh.version))
            else:
                sect.setsectiondescription(mh.start,"Mobipocket {0:d} Header".format(mh.version))
            mhname = os.path.join(files.outdir,"header.dat")
            print "Processing Mobipocket {0:d} section of book...".format(mh.version)

        if DUMP:
            # write out raw mobi header data
            open(pathof(mhname), 'wb').write(mh.header)

        # process each mobi header
        metadata = mh.getMetaData()
        mh.describeHeader(DUMP)
        if mh.isEncrypted():
            raise unpackException('Book is encrypted')

        resc = None
        pagemapproc = None
        obfuscate_data = []

        # first handle all of the different resource sections:  images, resources, fonts, and etc
        # build up a list of image names to use to postprocess the ebook

        print "Unpacking images, resources, fonts, etc"
        beg = mh.firstresource
        end = sect.num_sections
        if beg < K8Boundary:
            # processing first part of a combination file
            end = K8Boundary

        for i in xrange(beg, end):
            data = sect.loadSection(i)
            type = data[0:4]

            # handle the basics first
            if type in ["FLIS", "FCIS", "FDST", "DATP"]:
                if DUMP:
                    fname = type + "%05d" % i
                    if mh.isK8():
                        fname += "_K8"
                    fname += '.dat'
                    outname= os.path.join(files.outdir, fname)
                    open(pathof(outname), 'wb').write(data)
                    print "Dumping section {0:d} type {1:s} to file {2:s} ".format(i,type,outname)
                sect.setsectiondescription(i,"Type {0:s}".format(type))
                imgnames.append(None)
            elif type == "SRCS":
                imgnames = processSRCS(i, files, imgnames, sect, data)
            elif type == "PAGE":
                imgnames, pagemapproc = processPAGE(i, files, imgnames, sect, data, pagemapproc)
            elif type == "CMET":
                imgnames = processCMET(i, files, imgnames, sect, data)
            elif type == "FONT":
                imgnames, obfuscate_data = processFONT(i, files, imgnames, sect, data, obfuscate_data)
            elif type == "CRES":
                imgnames = processCRES(i, files, imgnames, sect, data)
            elif type == "CONT":
                imgnames = processCONT(i, files, imgnames, sect, data)
            elif type == "kind":
                imgnames = processkind(i, files, imgnames, sect, data)
            elif type == chr(0xa0) + chr(0xa0) + chr(0xa0) + chr(0xa0): 
                sect.setsectiondescription(i,"Empty_HD_Image/Resource_Placeholder")
                imgnames.append(None)
            elif type == "RESC":
                imgnames, resc = processRESC(i, files, imgnames, sect, data, resc)
            elif data == EOF_RECORD:
                sect.setsectiondescription(i,"End Of File")
                imgnames.append(None)
            elif data[0:8] == "BOUNDARY":
                sect.setsectiondescription(i,"BOUNDARY Marker")
                imgnames.append(None)
            else:
                # if reached here should be an image ow treat as unknown
                imgnames = processImage(i, files, imgnames, sect, data)

        # done unpacking resources
        # rename cover image to 'coverXXXXX.ext'
        imgnames = renameCoverImage(metadata, files, imgnames)

        # Print Replica
        if mh.isPrintReplica() and not k8only:
            createPrintReplica(metadata, files, imgnames, mh)
            continue

        # KF8 (Mobi 8)
        if mh.isK8():
            processMobi8(mh, metadata, sect, files, imgnames, pagemapproc, resc, obfuscate_data, apnxfile)

        # Old Mobi (Mobi 7)
        elif not k8only:
            processMobi7(mh, metadata, sect, files, imgnames)

        # process any remaining unknown sections of the palm file
        processUnknownSections(mh, sect, files, K8Boundary)

    return


def unpackBook(infile, outdir, apnxfile=None, dodump=False, dowriteraw=False, dosplitcombos=False):
    global DUMP
    global WRITE_RAW_DATA
    global SPLIT_COMBO_MOBIS
    if DUMP or dodump:
        DUMP = True
    if WRITE_RAW_DATA or dowriteraw:
        WRITE_RAW_DATA = True
    if SPLIT_COMBO_MOBIS or dosplitcombos:
        SPLIT_COMBO_MOBIS = True

    infile = utf8_str(infile)
    outdir = utf8_str(outdir)
    if apnxfile != None:
        apnxfile = utf8_str(apnxfile)

    files = fileNames(infile, outdir)

    # process the PalmDoc database header and verify it is a mobi
    sect = Sectionizer(infile)
    if sect.ident != 'BOOKMOBI' and sect.ident != 'TEXtREAd':
        raise unpackException('Invalid file format')
    if DUMP:
        sect.dumppalmheader()
    else:
        print "Palm DB type: %s, %d sections." % (sect.ident,sect.num_sections)

    # scan sections to see if this is a compound mobi file (K8 format)
    # and build a list of all mobi headers to process.
    mhlst = []
    mh = MobiHeader(sect,0)
    # if this is a mobi8-only file hasK8 here will be true
    mhlst.append(mh)
    K8Boundary = -1

    if mh.isK8():
        print "Unpacking a KF8 book..."
        hasK8 = True
    else:
        # This is either a Mobipocket 7 or earlier, or a combi M7/KF8
        # Find out which
        hasK8 = False
        for i in xrange(len(sect.sectionoffsets)-1):
            before, after = sect.sectionoffsets[i:i+2]
            if (after - before) == 8:
                data = sect.loadSection(i)
                if data == K8_BOUNDARY:
                    sect.setsectiondescription(i,"Mobi/KF8 Boundary Section")
                    mh = MobiHeader(sect,i+1)
                    hasK8 = True
                    mhlst.append(mh)
                    K8Boundary = i
                    break
        if hasK8:
            print "Unpacking a Combination M{0:d}/KF8 book...".format(mh.version)
            if SPLIT_COMBO_MOBIS:
                # if this is a combination mobi7-mobi8 file split them up
                mobisplit = mobi_split(infile)
                if mobisplit.combo:
                    outmobi7 = os.path.join(files.outdir, 'mobi7-'+files.getInputFileBasename() + '.mobi')
                    outmobi8 = os.path.join(files.outdir, 'mobi8-'+files.getInputFileBasename() + '.azw3')
                    open(pathof(outmobi7), 'wb').write(mobisplit.getResult7())
                    open(pathof(outmobi8), 'wb').write(mobisplit.getResult8())
        else:
            print "Unpacking a Mobipocket {0:d} book...".format(mh.version)

    if hasK8:
        files.makeK8Struct()

    process_all_mobi_headers(files, apnxfile, sect, mhlst, K8Boundary, False)

    if DUMP:
        sect.dumpsectionsinfo()
    return


def usage(progname):
    print ""
    print "Description:"
    print "  Unpacks an unencrypted Kindle/MobiPocket ebook to html and images"
    print "  or an unencrypted Kindle/Print Replica ebook to PDF and images"
    print "  into the specified output folder."
    print "Usage:"
    print "  %s -r -s -p apnxfile -d -h infile [outdir]" % progname
    print "Options:"
    print "    -r              write raw data to the output folder"
    print "    -s              split combination mobis into mobi7 and mobi8 ebooks"
    print "    -d              dump headers and other info to output and extra files"
    print "    -h              print this help message"
    print "    -p   apnxfile   apnx file associated with an azw3 infile"


def main():
    global DUMP
    global WRITE_RAW_DATA
    global SPLIT_COMBO_MOBIS
    print "kindleunpack v0.71 Experimental"
    print "   Based on initial mobipocket version Copyright © 2009 Charles M. Hannum <root@ihack.net>"
    print "   Extensive Extensions and Improvements Copyright © 2009-2014 "
    print "       by:  P. Durrant, K. Hendricks, S. Siebert, fandrieu, DiapDealer, nickredding, tkeo."
    print "   This program is free software: you can redistribute it and/or modify"
    print "   it under the terms of the GNU General Public License as published by"
    print "   the Free Software Foundation, version 3."

    argv=utf8_argv()
    progname = os.path.basename(argv[0])
    try:
        opts, args = getopt.getopt(argv[1:], "hdrsp:")
    except getopt.GetoptError, err:
        print str(err)
        usage(progname)
        sys.exit(2)

    if len(args)<1:
        usage(progname)
        sys.exit(2)

    apnxfile = None

    for o, a in opts:
        if o == "-d":
            DUMP = True
        if o == "-r":
            WRITE_RAW_DATA = True
        if o == "-s":
            SPLIT_COMBO_MOBIS = True
        if o == "-p":
            apnxfile = a
        if o == "-h":
            usage(progname)
            sys.exit(0)

    if len(args) > 1:
        infile, outdir = args
    else:
        infile = args[0]
        outdir = os.path.splitext(infile)[0]


    infileext = os.path.splitext(infile)[1].upper()
    if infileext not in ['.MOBI', '.PRC', '.AZW', '.AZW3', '.AZW4']:
        print "Error: first parameter must be a Kindle/Mobipocket ebook or a Kindle/Print Replica ebook."
        return 1

    try:
        print 'Unpacking Book...'
        unpackBook(infile, outdir, apnxfile)
        print 'Completed'

    except ValueError, e:
        print "Error: %s" % e
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
