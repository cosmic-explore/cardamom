import {
    LOGIN,
    JOIN_MATCH,
    REFRESH_MATCH,
    GET_CREATURE_MOVES,
    HOST_ROOT,
    GET_CREATURE_MOVE_ROUTE,
    SUBMIT_MATCH_COMMANDS,
    GET_STORED_COMMANDS
} from '../constants/server-endpoints'
import { CommandData } from '../DataTypes'

type positionQueryParams = {
    target_x: string
    target_y: string
}

const buildPostRequest = (body: string): RequestInit => {
    return {
        headers: {
            Accept: 'application/json',
            'Content-Type': 'application/json'
        },
        method: 'POST',
        body,
        credentials: 'include'
    }
}

const buildGetRequest = (): RequestInit => {
    return {
        headers: {
            Accept: 'application/json',
            'Content-Type': 'application/json'
        },
        method: 'GET',
        credentials: 'include'
    }
}

export const login = async (playerName: string) => {
    const requestBody = JSON.stringify({ player_name: playerName })
    const response = await fetch(LOGIN, buildPostRequest(requestBody))
    return response.json()
}

export const joinMatch = async (): Promise<EventSource> => {
    // return an EventSource for streaming match updates to the client
    return new EventSource(JOIN_MATCH, { withCredentials: true })
}

export const refreshMatch = async () => {
    /** Triggers a server sent event */
    await fetch(REFRESH_MATCH, buildGetRequest())
}

export const getCreatureMoves = async (creatureId: string) => {
    const url = `${GET_CREATURE_MOVES[0]}/${creatureId}/${GET_CREATURE_MOVES[1]}`
    const response = await fetch(url, buildGetRequest())
    return response.json()
}

export const getCreatureMoveRoute = async (
    creatureId: string,
    queryParams: positionQueryParams
) => {
    const url = `${GET_CREATURE_MOVE_ROUTE[0]}/${creatureId}/${GET_CREATURE_MOVE_ROUTE[1]}?${new URLSearchParams(queryParams)}`
    const response = await fetch(url, buildGetRequest())
    return response.json()
}

export const getActionTargets = async (creatureId: string, actionId: string) => {
    const url = `${HOST_ROOT}/creatures/${creatureId}/actions/${actionId}/targets`
    const response = await fetch(url, buildGetRequest())
    return response.json()
}

export const getActionAffected = async (
    creatureId: string,
    actionId: string,
    queryParams: positionQueryParams
) => {
    const url = `${HOST_ROOT}/creatures/${creatureId}/actions/${actionId}/affected?${new URLSearchParams(queryParams)}`
    const response = await fetch(url, buildGetRequest())
    return response.json()
}

export const submitMatchCommands = async (commands: CommandData[]) => {
    const requestBody = JSON.stringify({ commands })
    const response = await fetch(SUBMIT_MATCH_COMMANDS, buildPostRequest(requestBody))
    return response.ok
}

export const getStoredCommands = async (): Promise<CommandData[]> => {
    // Returns an empty array when commands have not been submitted
    const response = await fetch(GET_STORED_COMMANDS, buildGetRequest())
    return response.json()
}
