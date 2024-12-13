# -*- coding: utf-8 -*-

from se3_utilities import *
from ec_app_core import *
from se3_app_param import *

__author__ = 'fi11222'

class Se3_Passage(Se3ResponseBuilder):
    def __init__(self, p_app, p_requestHandler, p_context):
        super().__init__(p_app, p_requestHandler, p_context)
        self.m_logger.info('+++ Se3_Passage created')

    # -------------------------- Passage Response --------------------------------------------------------------------------
    def buildResponse(self):
        self.m_logger.info('Getting single verse response')
        self.m_logger.debug('self.m_previousContext: {0}'.format(self.m_previousContext))
        self.m_logger.debug('self.m_context: {0}'.format(self.m_context))
    
        # ---------------------- Parameter check ---------------------------------------------------------------------------
        l_response = self.m_app.passage_control(self.m_context)
    
        if len(l_response) > 0:
            return l_response, self.m_context, 'Error'
    
        l_uiLanguage = self.m_context['z']
        l_pcBookId = self.m_app.getBookFromAlias(self.m_context['b'].lower().strip())
        l_pcChapter = self.m_context['c']
        l_wholeChapter = (self.m_context['w'] == 'x')
    
        # verse start/end
        if l_wholeChapter:
            # whole chapter
            l_pcVerseStart = 1

            l_pcVerseEnd = self.m_app.getChapterVerseCount(l_pcBookId, int(l_pcChapter))
            #l_pcVerseEnd = self.m_app.m_bookChapter[l_pcBookId][int(l_pcChapter)]
        else:
            l_pcVerseStart = self.m_context['v']
            l_pcVerseEnd = self.m_context['w']
    
        l_dbConnection = self.m_app.getConnectionPool().getConnection()
        l_dbConnection.debugData = 'Se3_Passage.buildResponse main working connection'

        # get all attributes of the book the verse belongs to
        l_bibleQuran, l_idGroup0, l_idGroup1, l_bookPrev, l_bookNext, l_chapterShortEn, l_chapterShortFr = \
            self.m_app.getBookAttributes(l_pcBookId)
        #    self.m_app.m_bookChapter[l_pcBookId][0]
    
        # window title
        if l_wholeChapter:
            l_title = '{0} {1} {2}'.format(
                l_chapterShortFr if l_uiLanguage == 'fr' else l_chapterShortEn,
                l_pcChapter,
                EcAppParam.gcm_appTitle)
        else:
            l_title = '{0} {1}:{2}-{3} {4}'.format(
                l_chapterShortFr if l_uiLanguage == 'fr' else l_chapterShortEn,
                l_pcChapter,
                l_pcVerseStart,
                l_pcVerseEnd,
                EcAppParam.gcm_appTitle)
    
        # get chapter info
        l_chapterEn, l_chapterFr = self.m_app.get_chapter_names(self.m_context, l_dbConnection)
    
        l_groundStyle = 'pGroundHebrew'
        if l_idGroup0 == 'NT':
            l_groundStyle = 'pGroundGreek'
        elif l_idGroup0 == 'FT':
            l_groundStyle = 'pGroundArabic'
    
        # ---------------------- Top Banner --------------------------------------------------------------------------------
        l_topBannerTemplateString = """
            <div class="svTopBottom">
                <div class="svPrevLink">§{LeftComponent}</div>
                <div class="svNextLink">§{RightComponent}</div>
                <div class="svCenterLinks">§{CenterComponent}</div>
            </div>
        """
    
        l_topBannerTemplate = EcTemplate(l_topBannerTemplateString)
    
        # link for toggling between ground text display or not
        if self.m_context['g']:
            l_groundToggle = '<a href="" class="UnsetParameterLink TopLink" param="{1}">{0}</a>'.format(
                EcAppCore.get_user_string(self.m_context, 'p_hideGround'), Se3AppParam.gcm_pDisplayGround)
        else:
            l_groundToggle = '<a href="" class="SetParameterLink TopLink" param="{1}">{0}</a>'.format(
                EcAppCore.get_user_string(self.m_context, 'p_displayGround'), Se3AppParam.gcm_pDisplayGround)
    
        # link for toggling between parallel or ordinary display
        if self.m_context['r']:
            l_parallelToggle = '<a href="" class="UnsetParameterLink TopLink" param="{1}">{0}</a>'.format(
                EcAppCore.get_user_string(self.m_context, 'p_stackedVersions'), Se3AppParam.gcm_pParallel)
        else:
            l_parallelToggle = '<a href="" class="SetParameterLink TopLink" param="{1}">{0}</a>'.format(
                EcAppCore.get_user_string(self.m_context, 'p_parallelVersions'), Se3AppParam.gcm_pParallel)
    
        # whole chapter
        if not l_wholeChapter:
            # verse range = 1-x
            l_whole = self.makeLinkCommon(
                l_pcBookId, l_pcChapter, '1',
                EcAppCore.get_user_string(self.m_context, 'sv_wholeChapter') if l_idGroup0 != 'FT'
                else EcAppCore.get_user_string(self.m_context, 'sv_wholeSurah'),
                p_command='P',
                p_class='TopLink',
                p_v2='x')
        else:
            l_whole = ''
    
        if l_wholeChapter:
            # previous
            if l_pcChapter == '1':
                # previous book id since both verse and chapter are = 1
                l_previousBook = l_bookPrev
                # last chapter of the previous book
                #l_previousChapter = len(self.m_app.m_bookChapter[l_previousBook]) - 1
                l_previousChapter = self.m_app.chapterCount(l_previousBook)
            else:
                # same book
                l_previousBook = l_pcBookId
                # decrease chapter number since > 1
                l_previousChapter = int(l_pcChapter) - 1
    
            # next
            if l_pcChapter == str(self.m_app.chapterCount(l_pcBookId)):
                # last chapter = chapter count of the book = the element count of the list for this book minus one
                # --> first chapter of next book
                l_nextBook = l_bookNext
                l_nextChapter = 1
            else:
                l_nextBook = l_pcBookId
                # can just increase chapter count since not the last one of this book
                l_nextChapter = int(l_pcChapter) + 1
    
            # previous and next links
            # both contain 2 attribute for the new book/chapter value + one for the tooltip (title="")
            # both have 1-x as verse ranges since these are full chapters
            l_previousLink = self.makeLinkCommon(
                l_previousBook, l_previousChapter, '1', '◄',
                p_command='P',
                p_class='TopLink',
                p_v2='x',
                p_toolTip=EcAppCore.get_user_string(self.m_context, 'p_PreviousLink'))
    
            l_nextLink = self.makeLinkCommon(
                l_nextBook, l_nextChapter, '1', '►',
                p_command='P',
                p_class='TopLink',
                p_v2='x',
                p_toolTip=EcAppCore.get_user_string(self.m_context, 'p_NextLink'))
        else:
            l_previousLink = ''
            l_nextLink = ''
    
        # Final top banner assembly
        l_links = l_groundToggle + l_parallelToggle + l_whole
    
        l_topBanner = l_topBannerTemplate.safe_substitute(
            LeftComponent=l_previousLink,
            RightComponent=l_nextLink,
            CenterComponent=l_links
        )
    
        # ---------------------- Verses Display ----------------------------------------------------------------------------
        # version List
        l_versions = self.m_app.get_version_list(self.m_context)
    
        if self.m_context['r']:
            # +++++++++++++++++++++ Parallel Display +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
            l_response += '<table id="ParallelTable">\n'
            l_response += '<tr><td></td>\n'
    
            # column titles
            for l_versionId, l_versionLanguage, l_default, l_labelShort, l_labelTiny, l_basmalat in l_versions:
                l_chapterName = l_chapterFr if l_versionLanguage == 'fr' else l_chapterEn
                if not l_wholeChapter:
                    # not whole chapter
                    l_chapterName += ', ' + EcAppParam.gcm_userStrings[l_versionLanguage + '-' + 'p_VerseWord'] \
                        + 's ' + l_pcVerseStart \
                        + ' ' + EcAppParam.gcm_userStrings[l_versionLanguage + '-' + 'p_VerseTo'] \
                        + ' ' + l_pcVerseEnd
    
                # Display Chapter name (+ verses if applicable)
                l_response += '<td><p class="pChapterNameParallel">{0}</p>\n'.format(l_chapterName)
    
                # Display Version Name
                l_response += '<p class="pVersionNameParallel">{0}</p>\n'.format(l_labelShort)
    
                # Display Basmalat (if applicable)
                if len(l_basmalat) > 0 and l_wholeChapter and l_pcChapter not in ['1', '9']:
                    l_response += '<p class="pBasmalatParallel">{0}</p>\n'.format(l_basmalat)
    
                l_response += '</td>\n'
    
            if self.m_context['g']:
                # column title for ground text if displayed
                l_chapterName = (l_chapterFr if l_uiLanguage == 'fr' else l_chapterEn)
                if not l_wholeChapter:
                    # not whole chapter
                    l_chapterName += ', ' + EcAppCore.get_user_string(self.m_context, 'p_VerseWord') \
                        + 's ' + l_pcVerseStart \
                        + ' ' + EcAppCore.get_user_string(self.m_context, 'p_VerseTo') \
                        + ' ' + l_pcVerseEnd
    
                # Display Chapter name (+ verses if applicable)
                l_response += '<td><p class="pChapterNameParallel">{0}</p>\n'.format(l_chapterName)
    
                # Display Version Name
                l_response += '<p class="pVersionNameParallel">{0}</p>\n'.format(
                    EcAppCore.get_user_string(self.m_context, 'p_GroundText'))
    
                # Display Basmalat (if applicable)
                if l_pcBookId == 'Qur' and l_wholeChapter and l_pcChapter not in ['1', '9']:
                    l_response += '<p class="pBasmalatParallelAr">{0}</p>\n'.format('بِسْمِ اللَّهِ الرَّحْمَنِ الرَّحِيمِ')
    
                l_response += '</td>\n'
    
            # end of title row
            l_response += '</tr>\n'
    
            # Verse List -----------------------------------------------------------------------------------------------
            l_versionVector = self.m_app.get_version_vector(self.m_context)
            if self.m_context['g']:
                l_versionVector += ', "_gr"'
    
            l_query = """
                select
                    N.ID_VERSION
                    , N.ID_BOOK
                    , N.N_CHAPTER
                    , N.N_VERSE
                    , V.TX_VERSE_INSENSITIVE
                from
                    TB_VERSES_SQUARED N left outer join TB_VERSES V on
                        V.ID_VERSION = N.ID_VERSION
                        and V.ID_BOOK = N.ID_BOOK
                        and V.N_CHAPTER = N.N_CHAPTER
                        and V.N_VERSE = N.N_VERSE
                where
                    N.ID_VERSION in ({4})
                    and N.ID_BOOK = '{0}'
                    and N.N_CHAPTER = {1}
                    and N.N_VERSE >= {2}
                    and N.N_VERSE <= {3}
                order by N.N_VERSE, N.N_ORDER
                ;""".format(l_pcBookId, l_pcChapter, l_pcVerseStart, l_pcVerseEnd, l_versionVector)
    
            self.m_logger.debug('l_query {0}'.format(l_query))
            try:
                l_cursor = l_dbConnection.cursor(buffered=True)
                l_cursor.execute(l_query)
    
                if l_cursor.rowcount == 0:
                    return EcAppCore.get_user_string(self.m_context, 'e_noPassage').format(
                        self.m_context['b'], l_pcChapter), \
                           self.m_context, 'Error'
    
                # the version ID of the leftmost column
                l_versionLeft = l_versions[0][0]
                l_start = True
                for l_versionId, l_bookId, l_chapterNumber, l_verseNumber, l_verseText in l_cursor:
                    if l_versionId == l_versionLeft:
                        # the left-most column, with the verse references
                        if l_start:
                            l_start = False
                        else:
                            l_response += '</tr>'
    
                        # the right-click friendly link
                        l_jumpLink = self.makeLinkCommon(
                            l_bookId, l_chapterNumber, l_verseNumber,
                            '{0} {1}:{2}'.format(
                                l_chapterShortFr if l_uiLanguage == 'fr' else l_chapterShortEn,
                                l_chapterNumber,
                                l_verseNumber))
    
                        l_response += '<tr><td class="pVerseRef">' + l_jumpLink + '</td>'
    
                    # No verse text for this version
                    if l_verseText is None:
                        l_verseText = '<span class="pMessage">{0}</span>'.format(
                            EcAppCore.get_user_string(self.m_context, 'p_noText'))
    
                    if l_versionId == '_gr':
                        # ground text
                        l_verseText = '<span class="{0}">{1}</span>'.format(l_groundStyle, l_verseText)
                        l_response += '<td class="{0}">{1}</td>'.format(
                            'LRText' if l_idGroup0 == 'NT' else 'RLText', l_verseText)
                    else:
                        # Ordinary translation text
                        l_response += '<td><span class="TranslationText">{0}</span></td>'.format(l_verseText)
    
                l_response += '</tr>'
                l_cursor.close()
            except Exception as l_exception:
                self.m_logger.warning('Something went wrong {0}'.format(l_exception.args))
    
            # end of parallel table
            l_response += '</table>\n'
        else:
            # +++++++++++++++++++++ Stacked Display ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
            for l_versionId, l_versionLanguage, l_default, l_labelShort, l_labelTiny, l_basmalat in l_versions:
                l_chapterName = l_chapterFr if l_versionLanguage == 'fr' else l_chapterEn
                if not l_wholeChapter:
                    # not whole chapter
                    l_chapterName += ', ' + EcAppParam.gcm_userStrings[l_versionLanguage + '-' + 'p_VerseWord'] \
                        + 's ' + l_pcVerseStart \
                        + ' ' + EcAppParam.gcm_userStrings[l_versionLanguage + '-' + 'p_VerseTo'] \
                        + ' ' + l_pcVerseEnd
    
                # Display Chapter name (+ verses if applicable)
                l_response += '<h1 class="pChapterName">{0}</h1>\n'.format(l_chapterName)
    
                # Display Version Name
                l_response += '<h2 class="pVersionName">{0}</h2>\n'.format(l_labelShort)
    
                # Display Basmalat (if applicable)
                if len(l_basmalat) > 0 and l_wholeChapter and l_pcChapter not in ['1', '9']:
                    l_response += '<p class="pBasmalat">{0}</p>\n'.format(l_basmalat)
    
                # Verse List -----------------------------------------------------------------------------------------------
                l_query = """
                    select
                        TX_VERSE_INSENSITIVE
                        , N_VERSE
                    from TB_VERSES
                    where
                        ID_VERSION = '{4}'
                        and ID_BOOK = '{0}'
                        and N_CHAPTER = {1}
                        and N_VERSE >= {2}
                        and N_VERSE <= {3}
                    order by N_VERSE
                    ;""".format(l_pcBookId, l_pcChapter, l_pcVerseStart, l_pcVerseEnd, l_versionId)
    
                self.m_logger.debug('l_query {0}'.format(l_query))
                try:
                    l_cursor = l_dbConnection.cursor(buffered=True)
                    l_cursor.execute(l_query)
    
                    for l_verseText, l_verseNumber in l_cursor:
                        l_response += self.makeVerse(
                            l_pcBookId, l_pcChapter, l_verseNumber, l_verseText,
                            l_chapterShortFr if l_versionLanguage == 'fr' else l_chapterShortEn
                        )
    
                    l_cursor.close()
                except Exception as l_exception:
                    self.m_logger.warning('Something went wrong {0}'.format(l_exception.args))
    
            # Ground Text --------------------------------------------------------------------------------------------------
            if self.m_context['g']:
                l_chapterName = (l_chapterFr if l_uiLanguage == 'fr' else l_chapterEn)
                if not l_wholeChapter:
                    # not whole chapter
                    l_chapterName += ', ' + EcAppCore.get_user_string(self.m_context, 'p_VerseWord') \
                        + 's ' + l_pcVerseStart \
                        + ' ' + EcAppCore.get_user_string(self.m_context, 'p_VerseTo') \
                        + ' ' + l_pcVerseEnd
    
                # Display Chapter name (+ verses if applicable)
                l_response += '<h1 class="pChapterName">{0}</h1>\n'.format(l_chapterName)
    
                # Display Version Name
                l_response += '<h2 class="pVersionName">{0}</h2>\n'.format(
                    EcAppCore.get_user_string(self.m_context, 'p_GroundText')
                )
    
                # Display Basmalat (if applicable)
                if l_pcBookId == 'Qur' and l_wholeChapter and l_pcChapter not in ['1', '9']:
                    l_response += '<p class="pBasmalatAr">{0}</p>\n'.format('بِسْمِ اللَّهِ الرَّحْمَنِ الرَّحِيمِ')
    
                l_query = """
                    select
                        TX_VERSE_INSENSITIVE
                        , N_VERSE
                    from TB_VERSES
                    where
                        ID_BOOK = '{0}'
                        and N_CHAPTER = {1}
                        and N_VERSE >= {2}
                        and N_VERSE <= {3}
                        and ID_VERSION = '_gr'
                    order by N_VERSE
                    ;""".format(l_pcBookId, l_pcChapter, l_pcVerseStart, l_pcVerseEnd)
    
                self.m_logger.debug('l_query {0}'.format(l_query))
                try:
                    l_cursor = l_dbConnection.cursor(buffered=True)
                    l_cursor.execute(l_query)
    
                    for l_verseText, l_verseNumber in l_cursor:
                        # l_verseText = '<span class="{0}">{1}</span>'.format(l_groundStyle, l_verseText)
                        if l_idGroup0 == 'NT':
                            # left to right for Greek
                            l_response += self.makeVerse(
                                l_pcBookId, l_pcChapter, l_verseNumber, l_verseText,
                                l_chapterShortFr if l_uiLanguage == 'fr' else l_chapterShortEn)
                        else:
                            # right to left otherwise
                            l_response += self.makeVerse(
                                l_pcBookId, l_pcChapter, l_verseNumber, l_verseText,
                                l_chapterShortFr if l_uiLanguage == 'fr' else l_chapterShortEn, True)
    
                    l_cursor.close()
                except Exception as l_exception:
                    self.m_logger.warning('Something went wrong {0}'.format(l_exception.args))
    
        # ----------------- Final Page Assembly ----------------------------------------------------------------------------
    
        # top banner both at top and at bottom of single verse table
        l_response = l_topBanner + l_response + l_topBanner
    
        self.m_app.getConnectionPool().releaseConnection(l_dbConnection)
    
        return l_response, self.m_context, l_title
