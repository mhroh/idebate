import { google } from 'googleapis'
import { ChatConfig } from '../supabase/types'
import { supabaseAdmin } from '../supabase/client'

// Google Sheets API 클라이언트 초기화
const getGoogleSheetsClient = () => {
  const credentials = JSON.parse(process.env.GOOGLE_SHEETS_CREDENTIALS || '{}')

  const auth = new google.auth.GoogleAuth({
    credentials,
    scopes: ['https://www.googleapis.com/auth/spreadsheets'],
  })

  return google.sheets({ version: 'v4', auth })
}

/**
 * Google Sheets에서 설정 정보를 가져오고 캐싱합니다.
 * 캐시는 5분간 유효합니다.
 */
export async function getConfig(): Promise<ChatConfig> {
  try {
    // 1. 먼저 캐시에서 확인 (5분 이내)
    const { data: cachedConfig, error: cacheError } = await supabaseAdmin
      .from('config_cache')
      .select('*')
      .eq('config_key', 'chat_config')
      .single()

    if (!cacheError && cachedConfig) {
      const cacheAge = Date.now() - new Date(cachedConfig.updated_at).getTime()
      const fiveMinutes = 5 * 60 * 1000

      if (cacheAge < fiveMinutes) {
        console.log('📦 Using cached config')
        return JSON.parse(cachedConfig.config_value)
      }
    }

    // 2. 캐시 만료 또는 없음 → Google Sheets에서 가져오기
    console.log('🔄 Fetching config from Google Sheets')
    const sheets = getGoogleSheetsClient()
    const sheetId = process.env.GOOGLE_CONFIG_SHEET_ID!

    const response = await sheets.spreadsheets.values.get({
      spreadsheetId: sheetId,
      range: '정보!B:B',  // B열 전체
    })

    const data = response.data.values
    if (!data || data.length < 12) {
      throw new Error('Google Sheets 데이터가 불완전합니다.')
    }

    const config: ChatConfig = {
      serviceOnOff: data[1][0].toLowerCase() === 'on' ? 'on' : 'off',
      model: data[4][0],
      max_tokens: parseInt(data[5][0]),
      temperature: parseFloat(data[6][0]),
      system: data[8][0],
      a_p: data[9][0],
      e_p: data[10][0],
    }

    // 3. Supabase에 캐싱
    await supabaseAdmin
      .from('config_cache')
      .upsert({
        config_key: 'chat_config',
        config_value: JSON.stringify(config),
        updated_at: new Date().toISOString(),
      })

    return config
  } catch (error) {
    console.error('Error fetching config:', error)
    throw error
  }
}

/**
 * 학생 평가를 Google Sheets의 "수업요약" 시트에 저장합니다.
 */
export async function saveEvaluationToSheets(
  studentName: string,
  summary: string,
  grade: string
) {
  try {
    const sheets = getGoogleSheetsClient()
    const sheetId = process.env.GOOGLE_CONFIG_SHEET_ID!

    // 1. "수업요약" 시트에서 학생 이름 찾기
    const searchResponse = await sheets.spreadsheets.values.get({
      spreadsheetId: sheetId,
      range: '수업요약!A:A',
    })

    const studentColumn = searchResponse.data.values || []
    const studentRow = studentColumn.findIndex(
      (row) => row[0] === studentName
    )

    if (studentRow === -1) {
      // 학생이 없으면 새 행 추가
      await sheets.spreadsheets.values.append({
        spreadsheetId: sheetId,
        range: '수업요약!A:C',
        valueInputOption: 'RAW',
        requestBody: {
          values: [[studentName, summary, grade]],
        },
      })
    } else {
      // 학생이 있으면 업데이트
      const rowIndex = studentRow + 1
      await sheets.spreadsheets.values.update({
        spreadsheetId: sheetId,
        range: `수업요약!B${rowIndex}:C${rowIndex}`,
        valueInputOption: 'RAW',
        requestBody: {
          values: [[summary, grade]],
        },
      })
    }

    console.log(`✅ ${studentName} 평가 저장 완료`)
  } catch (error) {
    console.error('Error saving evaluation to sheets:', error)
    throw error
  }
}

/**
 * 캐시를 강제로 갱신합니다.
 */
export async function refreshConfigCache() {
  await supabaseAdmin
    .from('config_cache')
    .delete()
    .eq('config_key', 'chat_config')

  return await getConfig()
}
