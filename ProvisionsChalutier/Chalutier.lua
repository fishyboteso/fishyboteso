local FSH_STATE_WAITING = 0
local FSH_STATE_FISHING = 1
local FSH_STATE_GOT     = 2
local FSH_STATE_CAUGHT  = 3

local FSH_STATE_NAME = {
	"WAITING",
	"FISHING",
	"GOT",
	"CAUGHT"
}

local currentState
local function changeState(state, arg2)
	if currentState == state then return end

	if state == FSH_STATE_WAITING then
		if currentState == FSH_STATE_CAUGHT and not arg2 then return end
		ProvCha.UI.Icon:SetTexture("ProvisionsChalutier/textures/icon_dds/waiting.dds")
		ProvCha.UI.blocInfo:SetColor(0.3961, 0.2706, 0)

		EVENT_MANAGER:UnregisterForUpdate(ProvCha.name .. "antiJobFictif")
		EVENT_MANAGER:UnregisterForEvent(ProvCha.name .. "OnSlotUpdate", EVENT_INVENTORY_SINGLE_SLOT_UPDATE)
	elseif state == FSH_STATE_FISHING then
		ProvCha.UI.Icon:SetTexture("ProvisionsChalutier/textures/icon_dds/fishing.dds")
		ProvCha.UI.blocInfo:SetColor(0.2980, 0.6118, 0.8392)

		EVENT_MANAGER:RegisterForEvent(ProvCha.name .. "OnSlotUpdate", EVENT_INVENTORY_SINGLE_SLOT_UPDATE, Chalutier_OnSlotUpdate)
	elseif state == FSH_STATE_GOT then
		ProvCha.UI.Icon:SetTexture("ProvisionsChalutier/textures/icon_dds/got.dds")
		ProvCha.UI.blocInfo:SetColor(0, 0.8, 0)

		EVENT_MANAGER:RegisterForUpdate(ProvCha.name .. "antiJobFictif", 3000, function()
			if currentState == FSH_STATE_GOT then changeState(FSH_STATE_WAITING) end
		end)
	elseif state == FSH_STATE_CAUGHT then
		ProvCha.UI.Icon:SetTexture("ProvisionsChalutier/textures/icon_dds/in_bag.dds")
		ProvCha.UI.blocInfo:SetColor(0.3961, 0.2706, 0)

		EVENT_MANAGER:UnregisterForUpdate(ProvCha.name .. "antiJobFictif")
		EVENT_MANAGER:UnregisterForEvent(ProvCha.name .. "OnSlotUpdate", EVENT_INVENTORY_SINGLE_SLOT_UPDATE)
		
		EVENT_MANAGER:RegisterForUpdate(ProvCha.name .. "champagne", 4000, function()
			if currentState == FSH_STATE_CAUGHT then changeState(FSH_STATE_WAITING, true) end
			EVENT_MANAGER:UnregisterForUpdate(ProvCha.name .. "champagne")
		end)
	end
	--d(FSH_STATE_NAME[state + 1])
	currentState = state
end

function Chalutier_OnSlotUpdate(event, bagId, slotIndex, isNew)
	if currentState == FSH_STATE_FISHING then
		changeState(FSH_STATE_GOT)
	elseif currentState == FSH_STATE_GOT then
		changeState(FSH_STATE_CAUGHT)
	end
end

local currentInteractableName
function Chalutier_OnAction()
	local action, interactableName, _, _, additionalInfo = GetGameCameraInteractableActionInfo()

	if action then
		local state = FSH_STATE_WAITING

		if additionalInfo == ADDITIONAL_INTERACT_INFO_FISHING_NODE then
			currentInteractableName = interactableName

			ProvCha.UI.blocInfo:SetHidden(false)
		elseif currentInteractableName == interactableName then
			if currentState > FSH_STATE_FISHING then return end

			state = FSH_STATE_FISHING
		end

		changeState(state)
	elseif currentState ~= FSH_STATE_WAITING then
		changeState(FSH_STATE_WAITING)
		ProvCha.UI.blocInfo:SetHidden(true)
	else
		ProvCha.UI.blocInfo:SetHidden(true)
	end
end

local function Chalutier_OnAddOnLoad(eventCode, addOnName)
	if (ProvCha.name ~= addOnName) then return end

	ProvCha.vars = ZO_SavedVars:NewAccountWide("ProvChaSV", 1, nil, ProvCha.defaults)

	ProvCha.UI = WINDOW_MANAGER:CreateControl(nil, GuiRoot, CT_TOPLEVELCONTROL)
	ProvCha.UI:SetMouseEnabled(true)
	ProvCha.UI:SetClampedToScreen(true)
	ProvCha.UI:SetMovable(true)
	ProvCha.UI:SetDimensions(64, 92)
	ProvCha.UI:SetDrawLevel(0)
	ProvCha.UI:SetDrawLayer(0)
	ProvCha.UI:SetDrawTier(0)

	ProvCha.UI:SetHidden(not ProvCha.vars.enabled)
	ProvCha.UI:ClearAnchors()
	ProvCha.UI:SetAnchor(TOPLEFT, GuiRoot, TOPLEFT, 0, 0)

	ProvCha.UI.blocInfo = WINDOW_MANAGER:CreateControl(nil, ProvCha.UI, CT_TEXTURE)
	ProvCha.UI.blocInfo:SetDimensions(64, 6)
	ProvCha.UI.blocInfo:SetColor(0.396, 0.27, 0)
	ProvCha.UI.blocInfo:SetAnchor(TOP, ProvCha.UI, TOP, 0, blocInfo)
	ProvCha.UI.blocInfo:SetHidden(true)
	ProvCha.UI.blocInfo:SetDrawLevel(2)

	ProvCha.UI.Icon = WINDOW_MANAGER:CreateControl(nil, ProvCha.UI, CT_TEXTURE)
	ProvCha.UI.Icon:SetBlendMode(TEX_BLEND_MODE_ALPHA)
	ProvCha.UI.Icon:SetTexture("ProvisionsChalutier/textures/icon_dds/waiting.dds")
	ProvCha.UI.Icon:SetDimensions(64, 64)
	ProvCha.UI.Icon:SetAnchor(TOPLEFT, ProvCha.UI, TOPLEFT, 0, 18)
	ProvCha.UI.Icon:SetHidden(false)
	ProvCha.UI.Icon:SetDrawLevel(2)

	local fragment = ZO_SimpleSceneFragment:New(ProvCha.UI)
	SCENE_MANAGER:GetScene('hud'):AddFragment(fragment)
	SCENE_MANAGER:GetScene('hudui'):AddFragment(fragment)

	EVENT_MANAGER:UnregisterForEvent(ProvCha.name, EVENT_ADD_ON_LOADED)

	ZO_PreHookHandler(RETICLE.interact, "OnEffectivelyShown", Chalutier_OnAction)
	ZO_PreHookHandler(RETICLE.interact, "OnHide", Chalutier_OnAction)
end

EVENT_MANAGER:RegisterForEvent(ProvCha.name, EVENT_ADD_ON_LOADED, function(...) Chalutier_OnAddOnLoad(...) end)
