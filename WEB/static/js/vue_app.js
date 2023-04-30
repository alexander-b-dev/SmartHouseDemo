const sensor = {
    delimiters: ['[[', ']]'],
    props: {
        alert: Boolean,
        img: String,
        value: String,
        alias: String,
        name: String
    },
    data() {
        return {
            editMode: false,
            newAlias: "",
            threshold: "",
            thresholdCondition: "="
        }
    },

    methods: {
        goToEditMode() {
            $.ajax({
                url: `/threshold/${this.name.replaceAll("/", "~")}`,
                contentType: "application/json",
                type: "GET",
                success: (data) => {
                    dt = JSON.parse(data)
                    this.threshold = dt[1]
                    this.thresholdCondition = dt[0]
                    this.newAlias = this.alias
                    this.editMode = true;
                }
            });
        },

        goToNormalMode() {
            this.editMode = false;
        },

        save() {
            if (this.alias != this.newAlias) {
                $.ajax({
                    url: "/user/config/sensor",
                    contentType: "application/json",
                    type: "PUT",
                    data: JSON.stringify({
                        sensor: this.name,
                        alias: this.newAlias,
                        visibility: true
                    }),
                    success: () => {
                        this.$root.getConf();
                    }
                });
            }

            $.ajax({
                url: `/threshold/${this.name.replaceAll("/", "~")}`,
                contentType: "application/json",
                type: "PUT",
                data: JSON.stringify({
                    condition: this.thresholdCondition,
                    value: this.threshold
                })
            });
            this.goToNormalMode()
        },

        hide() {
            $.ajax({
                url: "/user/config/sensor",
                contentType: "application/json",
                type: "PUT",
                data: JSON.stringify({
                    sensor: this.name,
                    alias: this.newAlias,
                    visibility: false
                }),
                success: () => {
                    this.$root.getConf();
                    this.goToNormalMode()
                }
            });
        }

    },

    template: `
    <div class="sensor">
        <div class="sensorTileNormal" :class="{sensorTileAlert: alert}" @click="goToEditMode">
            <template v-if="!this.editMode">
                <div class="sensorAlias">
                    [[alias]]
                </div>
                <div class="sensorPic">
                    <img style="height: 5vh" :src="img">
                </div>
                <div class="sensorVal">
                    [[value]]
                </div>
            </template>
            <template v-else>
                <div style="padding:5px; height:100%; background-color: #202020; display: flex; flex-direction: column; justify-content: space-evenly;" @click.stop="">
                    <div style="background-color: inherit">
                        <button style="float: right; padding:0; width: 3vw;" @click.stop="goToNormalMode">X</button>
                    </div>
                    <p class="settingsText">Alias:</p>
                    <input type="text" style="width: calc(14.2vw - 10px);" v-model="newAlias">
                    <p class="settingsText" style="margin-top: 5px">Threshold</p>
                    <div style="display: flex; background-color: inherit; justify-content: space-between;">
                        <select style="width:4vw" v-model="thresholdCondition">
                            <option>=</option>
                            <option>&gt</option>
                            <option>&lt</option>
                        </select>
                        <input type="text" style="width:8vw" v-model="threshold">
                    </div>
                    <div style="background-color: inherit; display: flex; flex-direction: row-reverse; justify-content: space-between; margin-top: 5px">
                        <button style="padding:3px; width: 5vw;" @click.stop="save">Ok</button>
                        <button style="padding:3px; width: 5vw;" @click.stop="hide">Hide</button>
                    </div>
                </div>
            </template>
        </div>
    </div>`
}

const sensorsContainer = {
    components: {
        'sensor': sensor
    },
    props: {
        sensors: Array,
    },
    data() {
        return { sensorsData: [] }
    },

    template: `
        <div class="sensorsContainer">
            <sensor v-for="sensor in sensors" :alias="sensor.alias" :alert="sensor.alert" 
            :img="sensor.img" :value="sensor.value" :name="sensor.name"></sensor>
        </div>`
}

const sensorAlert = {
    delimiters: ['[[', ']]'],
    props: {
        sensor: String,
    },
    template: `
    <div class="alert"><p class="alertText">[[sensor]] out of bounds</p></div>`
}

const sensorSetting = {
    delimiters: ['[[', ']]'],
    props: {
        sensor: String,
        alias: String
    },

    methods:{
        restoreSensor(){
            $.ajax({
                url: "/user/config/sensor",
                contentType: "application/json",
                type: "PUT",
                data: JSON.stringify({
                    sensor: this.sensor,
                    alias: this.alias,
                    visibility: true
                }),
                success: () => {
                    this.$root.getConf()
                }
            });
        }
    },
    template: `
        <div class="sensorAlias" style="font-size: 16;">
            [[this.alias]]
        </div>
        <button style="margin: 10px;" @click.stop="restoreSensor">Restore</button>`
}

const rootApp = Vue.createApp({
    delimiters: ['[[', ']]'],
    data() {
        return {
            showSettings: false,
            sensorTypes: [],
            alerts: [],
            tempName: "",
            clientConfig: {
                userName: "Default user",
                sensorsConfig: {}
            }
        }
    },
    methods: {
        update(data) {
            this.sensorTypes = []
            for (const sensorType in data) {
                typeArr = []
                for (var sensor of data[sensorType]) {
                    if (sensor.name in this.clientConfig.sensorsConfig) {
                        if (this.clientConfig.sensorsConfig[sensor.name].visibility) {
                            if (this.clientConfig.sensorsConfig[sensor.name].alias != "") {
                                sensor.alias = this.clientConfig.sensorsConfig[sensor.name].alias
                            }
                            else {
                                sensor.alias = sensor.name.split("/")[2]
                            }
                            typeArr.push(sensor)
                        }
                    }
                    else {
                        sensor.alias = sensor.name.split("/")[2]
                        typeArr.push(sensor)
                    }
                }
                if (typeArr.length > 0) {
                    this.sensorTypes.push(typeArr)
                }
            }
        },

        addAlerts(sensorAlerts) {
            for (const alert of sensorAlerts) {
                let alias = alert.split("/")[2]
                if (alert in this.clientConfig.sensorsConfig) {
                    if (this.clientConfig.sensorsConfig[alert].visibility) {
                        if (this.clientConfig.sensorsConfig[alert].alias != "") {
                            alias = this.clientConfig.sensorsConfig[alert].alias
                        }
                        this.alerts.push(alias)
                        setTimeout(this.delAlert, 5000)
                    }
                }
                else {
                    this.alerts.push(alias)
                    setTimeout(this.delAlert, 5000)
                }
            }
        },

        delAlert() {
            this.alerts.splice(0, 1)
        },

        getConf() {
            $.ajax({
                url: '/user/config',
                contentType: "application/json",
                type: "GET",
                success: (data) => {
                    this.clientConfig = JSON.parse(data)
                },
            });
        },

        openSettings(){
            this.showSettings = true
            this.tempName = this.clientConfig.userName
        },

        setUserName(){
            $.ajax({
                url: '/user/config/name',
                contentType: "application/json",
                type: "PUT",
                data: JSON.stringify({
                    name: this.tempName
                }),
                success: () =>{
                    this.clientConfig.userName = this.tempName
                    alert("Saved")
                }
            });
        },

        getData() {
            $.ajax({
                url:'/data',
                type: "GET",
                success: (data) => {
                    data = JSON.parse(data)
                    this.update(data.sensorTypes)
                    setTimeout(() => { this.getData() }, 2000)
                },
            });
        }
    },

    mounted() {
        this.getConf()
        this.getData()
    }
})

rootApp.component('sensors-container', sensorsContainer)
rootApp.component('sensor-alert', sensorAlert)
rootApp.component('sensor-setting', sensorSetting)
