<!--
Copyright: Ankitects Pty Ltd and contributors
License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html
-->
<script lang="ts">
    import type { GraphsResponse } from "@generated/anki/stats_pb";
    import * as tr from "@generated/ftl";
    import { HelpPage } from "@tslib/help-page";
    import HelpModal from "$lib/components/HelpModal.svelte";
    import type Carousel from "bootstrap/js/dist/carousel";
    import type Modal from "bootstrap/js/dist/modal";
    import type { HelpItem } from "$lib/components/types";

    import { type RevlogRange } from "./graph-helpers";
    import { DisplayMode, type PeriodTrueRetentionData, Scope } from "./true-retention";

    import Graph from "./Graph.svelte";
    import InputBox from "./InputBox.svelte";
    import TrueRetentionCombined from "./TrueRetentionCombined.svelte";
    import TrueRetentionSingle from "./TrueRetentionSingle.svelte";
    import { assertUnreachable } from "@tslib/typing";

    interface Props {
        revlogRange: RevlogRange;
        sourceData: GraphsResponse | null;
    }

    const { revlogRange, sourceData = null }: Props = $props();

    const retentionData: PeriodTrueRetentionData | null = $derived.by(() => {
        if (sourceData === null) {
            return null;
        } else {
            // Assert that all the True Retention data will be defined
            return sourceData.trueRetention as PeriodTrueRetentionData;
        }
    });

    const retentionHelp = {
        trueRetention: {
            title: tr.statisticsTrueRetentionTitle(),
            help: tr.statisticsTrueRetentionTooltip(),
        },
    };

    const helpSections: HelpItem[] = Object.values(retentionHelp);

    let modal: Modal;
    let carousel: Carousel;

    function openHelpModal(index: number): void {
        modal.show();
        carousel.to(index);
    }

    let mode: DisplayMode = $state(DisplayMode.Summary);

    const title = tr.statisticsTrueRetentionTitle();
    const subtitle = tr.statisticsTrueRetentionSubtitle();
    const onTitleClick = () => {
        openHelpModal(Object.keys(retentionHelp).indexOf("trueRetention"));
    };
</script>

<Graph {title} {subtitle} {onTitleClick}>
    <HelpModal
        title={tr.statisticsTrueRetentionTitle()}
        url={HelpPage.DeckOptions.fsrs}
        slot="tooltip"
        {helpSections}
        on:mount={(e) => {
            modal = e.detail.modal;
            carousel = e.detail.carousel;
        }}
    />
    <InputBox>
        <label>
            <input type="radio" bind:group={mode} value={DisplayMode.Young} />
            {tr.statisticsTrueRetentionYoung()}
        </label>

        <label>
            <input type="radio" bind:group={mode} value={DisplayMode.Mature} />
            {tr.statisticsTrueRetentionMature()}
        </label>

        <label>
            <input type="radio" bind:group={mode} value={DisplayMode.Summary} />
            {tr.statisticsTrueRetentionAll()}
        </label>
    </InputBox>

    <div class="table-container">
        {#if retentionData === null}
            <div>{tr.statisticsNoData()}</div>
        {:else if mode === DisplayMode.Young}
            <TrueRetentionSingle
                {revlogRange}
                data={retentionData}
                scope={Scope.Young}
            />
        {:else if mode === DisplayMode.Mature}
            <TrueRetentionSingle
                {revlogRange}
                data={retentionData}
                scope={Scope.Mature}
            />
        {:else if mode === DisplayMode.All}
            <TrueRetentionSingle {revlogRange} data={retentionData} scope={Scope.All} />
        {:else if mode === DisplayMode.Summary}
            <TrueRetentionCombined {revlogRange} data={retentionData} />
        {:else}
            {assertUnreachable(mode)}
        {/if}
    </div>
</Graph>

<style>
    .table-container {
        margin-top: 1rem;
        overflow-x: auto;

        display: flex;
        align-items: center;
    }
</style>
