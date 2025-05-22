import {
    LOGIN,
    JOIN_MATCH,
    REFRESH_MATCH,
    GET_CREATURE_MOVES,
    HOST_ROOT
} from '../constants/server-endpoints'

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

export const getActionTargets = async (creatureId: string, actionId: string) => {
    const url = `${HOST_ROOT}/creatures/${creatureId}/actions/${actionId}/targets`
    const response = await fetch(url, buildGetRequest())
    return response.json()
}

type positionQueryParams = {
    target_x: string
    target_y: string
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
