export const HOST_ROOT = `${import.meta.env.VITE_HOST_ROOT}/api`

export const LOGIN = `${HOST_ROOT}/login`
export const GET_PLAYER_MATCHES = `${HOST_ROOT}/player/matches`
export const JOIN_MATCH = `${HOST_ROOT}/match/join`
export const REFRESH_MATCH = `${HOST_ROOT}/match/refresh`
export const GET_CREATURE_MOVES = [`${HOST_ROOT}/creaturestates`, 'moves']
export const GET_CREATURE_MOVE_ROUTE = [`${HOST_ROOT}/creaturestates`, 'moves/route']
export const SUBMIT_MATCH_COMMANDS = `${HOST_ROOT}/match/submit`
export const GET_STORED_COMMANDS = `${HOST_ROOT}/match/commands`
